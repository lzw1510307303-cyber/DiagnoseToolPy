import { Routes, Route } from 'react-router-dom';
import './styles.css';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import AnalysisTasksPage from './pages/AnalysisTasksPage';
import TaskDetailPage from './pages/TaskDetailPage';
import CasebasePage from './pages/CasebasePage';
import CaseDetailPage from './pages/CaseDetailPage';
import SettingsPage from './pages/SettingsPage';
import AIDiagnosisPage from './pages/AIDiagnosisPage';
import LogSearchPage from './pages/LogSearchPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="analysis" element={<AnalysisTasksPage />} />
        <Route path="analysis/:taskId" element={<TaskDetailPage />} />
        <Route path="cases" element={<CasebasePage />} />
        <Route path="cases/:caseId" element={<CaseDetailPage />} />
        <Route path="diagnosis" element={<AIDiagnosisPage />} />
        <Route path="logs" element={<LogSearchPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
