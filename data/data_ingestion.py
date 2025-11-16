"""
Data ingestion script for the names web application.
Extracts CSV files from a ZIP archive and loads them into an SQLITE database.
"""

import sqlite3
import zipfile
import csv
from pathlib import Path
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

arguments = argparse.ArgumentParser(description="Ingest CSV data from a ZIP file into an SQLITE database.")
arguments.add_argument("--download", action="store_true", help="Download the ZIP file before ingestion.")
arguments = arguments.parse_args()

NAMES_ZIP = "names.zip"
NAMES_BY_STATE_ZIP = "namesbystate.zip"


class NamesDataPipeline:
    def __init__(self, db_path='../names_database.db'):
        """
        Initialize the data pipeline.
        
        Args:
            db_path: Path to SQLite database file
            zip_path: Path to the names zip file
        """
        self.db_path = Path(db_path)
        self.zip_path = Path(NAMES_ZIP)
        self.names_by_state_zip_path = Path(NAMES_BY_STATE_ZIP)
        self.conn = None
        self.cursor = None
        
    def init_database(self):
        """Initialize the database schema by executing initdb.sql"""
        logger.info("Initializing database schema...")
        
        # Execute SQL schema file
        try:
            with open('initdb.sql', 'r') as sql_file:
                sql_script = sql_file.read()
        except (FileNotFoundError, IOError) as e:
            logger.error(f"Could not open 'initdb.sql' for reading. Expected at: {Path('initdb.sql').resolve()}")
            logger.error(f"Error details: {e}")
            raise
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.executescript(sql_script)
        self.conn.commit()
        
        logger.info("Database schema initialized successfully.")
    
    def extract_and_load_states(self):
        """Extract CSV files for names by state from zip and load into database"""
        logger.info(f"Opening zip file: {self.names_by_state_zip_path}")
        
        total_records = 0
        files_processed = 0
        with zipfile.ZipFile(self.names_by_state_zip_path, 'r') as zip_ref:
            # Get list of CSV files in the zip
            csv_files = [f for f in zip_ref.namelist() if f.lower().endswith('.txt') or f.lower().endswith('.csv')]
            logger.info(f"Found {len(csv_files)} data files in zip archive.")
            
            for filename in csv_files:
                logger.info(f"Processing {filename}")
                
                # Read CSV data from zip file
                with zip_ref.open(filename) as csv_file:
                    # SSA files are comma
                    csv_text = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_text)
                    # Prepare batch insert
                    records = []
                    for row in reader:
                        if len(row) == 5:  # state
                            state, gender, year, name, count = row
                            records.append((state, name, gender, int(count), int(year)))
                    # Batch insert for performance
                    self.cursor.executemany(
                        "INSERT INTO ssa_names_by_state (state, name, gender, count, year) VALUES (?, ?, ?, ?, ?)",
                        records
                    )
                    self.conn.commit()

                    total_records += len(records)
                    files_processed += 1
                    logger.info(f"  Inserted {len(records)} records from {filename}")


    def extract_and_load(self):
        """Extract CSV files from zip and load into database"""
        logger.info(f"Opening zip file: {self.zip_path}")
        
        total_records = 0
        files_processed = 0
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            # Get list of CSV files in the zip
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.txt') or f.endswith('.csv')]
            logger.info(f"Found {len(csv_files)} data files in zip archive.")
            
            for filename in csv_files:
                # Extract year from filename (e.g., yob1880.txt -> 1880)
                year = self._extract_year_from_filename(filename)
                
                if year is None:
                    logger.warning(f"Skipping file {filename}: Could not extract year")
                    continue
                
                logger.info(f"Processing {filename} (Year: {year})")
                
                # Read CSV data from zip file
                with zip_ref.open(filename) as csv_file:
                    # SSA files are comma-separated: name,gender,count
                    csv_text = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_text)
                    
                    # Prepare batch insert
                    records = []
                    for row in reader:
                        if len(row) == 3:  # name, gender, count
                            name, gender, count = row
                            records.append((name, gender, int(count), year))
                    
                    # Batch insert for performance
                    self.cursor.executemany(
                        "INSERT INTO ssa_names_states (name, gender, count, year) VALUES (?, ?, ?, ?)",
                        records
                    )
                    self.conn.commit()
                    
                    total_records += len(records)
                    files_processed += 1
                    logger.info(f"  Inserted {len(records)} records from {filename}")
        
        logger.info(f"Data ingestion complete! Processed {files_processed} files, inserted {total_records} records.")
    
    def _extract_year_from_filename(self, filename):
        """
        Extract year from filename like 'yob1880.txt' or 'yob2021.txt'
        
        Args:
            filename: The filename to parse
            
        Returns:
            Year as integer or None if not found
        """
        import re
        match = re.search(r'(\d{4})', filename)
        return int(match.group(1)) if match else None

    def create_indexes(self, table_name='ssa_names'):
        """Create database indexes for better query performance"""
        logger.info("Creating database indexes...")
        
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_name ON {table_name}(name);",
            f"CREATE INDEX IF NOT EXISTS idx_year ON {table_name}(year);",
            f"CREATE INDEX IF NOT EXISTS idx_name_year ON {table_name}(name, year);",
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
        
        self.conn.commit()
        logger.info("Indexes created successfully.")
    
    def verify_data(self, table_name='ssa_names'):
        """Verify data was loaded correctly"""
        logger.info("Verifying data...")
        
        # Count total records
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = self.cursor.fetchone()[0]
        logger.info(f"Total records: {total:,}")
        
        # Count distinct years
        self.cursor.execute(f"SELECT COUNT(DISTINCT year) FROM {table_name}")
        years = self.cursor.fetchone()[0]
        logger.info(f"Years covered: {years}")
        
        # Sample data
        self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        samples = self.cursor.fetchall()
        logger.info("Sample records:")
        for row in samples:
            logger.info(f"  {row}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
    
    def run(self):
        """Run the complete pipeline"""
        try:
            self.init_database()
            self.extract_and_load()
            self.create_indexes()
            self.verify_data()

            self.extract_and_load_states()
            self.create_indexes(table_name='ssa_names_by_state')
            self.verify_data(table_name='ssa_names_by_state')
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
        finally:
            self.close()


if __name__ == "__main__":
    # Run the pipeline
    pipeline = NamesDataPipeline(db_path='../names_database.db')
    pipeline.run()
