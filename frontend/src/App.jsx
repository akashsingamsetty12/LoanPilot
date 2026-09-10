/**
 * LoanPilot — App Entry Point
 * ==============================
 * Root component with React Router and Layout.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import NewApplication from './pages/NewApplication';
import ApplicationReview from './pages/ApplicationReview';
import ReportView from './pages/ReportView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="applications/new" element={<NewApplication />} />
          <Route path="applications/:id" element={<ApplicationReview />} />
          <Route path="applications/:id/report" element={<ReportView />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
