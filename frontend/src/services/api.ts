import axios from 'axios';

const API_BASE_URL = '/api/v1';

// API Client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Job types
export interface Job {
  id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  original_filename: string;
  created_at: string;
  updated_at: string;
  output_path: string | null;
  error_message: string | null;
}

export interface JobsList {
  jobs: Job[];
  total: number;
}

export interface JobResult {
  url: string;
  expires_in_seconds: number;
}

// API Methods
export const api = {
  // Upload a new sketch file
  uploadSketch: async (file: File): Promise<Job> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<Job>('/jobs', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get a specific job
  getJob: async (jobId: number): Promise<Job> => {
    const response = await apiClient.get<Job>(`/jobs/${jobId}`);
    return response.data;
  },

  // Get all jobs
  getJobs: async (skip = 0, limit = 100): Promise<JobsList> => {
    const response = await apiClient.get<JobsList>('/jobs', {
      params: { skip, limit },
    });
    return response.data;
  },

  // Get the result URL for a completed job
  getJobResult: async (jobId: number): Promise<JobResult> => {
    const response = await apiClient.get<JobResult>(`/result/${jobId}`);
    return response.data;
  },
};
