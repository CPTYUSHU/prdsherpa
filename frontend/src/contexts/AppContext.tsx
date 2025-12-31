import React, { createContext, useContext, useState, useEffect } from 'react';
import type { Project } from '../types';
import { projectApi } from '../services/api';

interface AppContextType {
  projects: Project[];
  currentProject: Project | null;
  loading: boolean;
  setCurrentProject: (project: Project | null) => void;
  refreshProjects: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(false);

  const refreshProjects = async () => {
    setLoading(true);
    try {
      const data = await projectApi.list();
      setProjects(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshProjects();
  }, []);

  return (
    <AppContext.Provider
      value={{
        projects,
        currentProject,
        loading,
        setCurrentProject,
        refreshProjects,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

