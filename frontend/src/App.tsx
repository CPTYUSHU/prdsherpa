import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from './components/Layout/MainLayout';
import Welcome from './pages/Welcome';
import NewProject from './pages/NewProject';
import KnowledgeBase from './pages/KnowledgeBase';
import Requirements from './pages/Requirements';
import Chat from './pages/Chat';
import WireframePreview from './pages/WireframePreview';
import APIKeySettings from './components/APIKeySettings';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Welcome />} />
            <Route path="settings/api-keys" element={<APIKeySettings />} />
            <Route path="project/new" element={<NewProject />} />
            <Route path="project/:projectId" element={<Requirements />} />
            <Route path="project/:projectId/requirements" element={<Requirements />} />
            <Route path="project/:projectId/requirement/:conversationId" element={<Chat />} />
            <Route path="project/:projectId/kb" element={<KnowledgeBase />} />
            <Route path="project/:projectId/knowledge" element={<KnowledgeBase />} />
            <Route path="project/:projectId/wireframe/:conversationId" element={<WireframePreview />} />
            {/* 兼容旧路由 */}
            <Route path="project/:projectId/chat" element={<Chat />} />
            <Route path="project/:projectId/chat/:conversationId" element={<Chat />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  );
}

export default App;
