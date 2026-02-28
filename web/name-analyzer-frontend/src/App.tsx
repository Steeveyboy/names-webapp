import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import NameAnalyzerPage from './pages/NameAnalyzerPage';
import FactsPage from './pages/FactsPage';
import EtymologyPage from './pages/EtymologyPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<NameAnalyzerPage />} />
          <Route path="/facts" element={<FactsPage />} />
          <Route path="/etymology" element={<EtymologyPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
