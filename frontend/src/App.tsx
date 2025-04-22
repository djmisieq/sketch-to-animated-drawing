import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Header from '@/components/Header'
import HomePage from '@/pages/HomePage'
import UploadPage from '@/pages/UploadPage'
import StatusPage from '@/pages/StatusPage'
import DownloadPage from '@/pages/DownloadPage'
import NotFoundPage from '@/pages/NotFoundPage'

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow container mx-auto py-6 px-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/status/:jobId" element={<StatusPage />} />
          <Route path="/download/:jobId" element={<DownloadPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <Toaster />
    </div>
  )
}

export default App
