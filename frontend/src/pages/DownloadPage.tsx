import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, Loader2, ArrowLeft, FileVideo } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { api, Job, JobResult } from '@/services/api';
import { formatDate } from '@/lib/utils';

const DownloadPage = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [resultLoading, setResultLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchJob = async () => {
      if (!jobId) return;
      
      try {
        const fetchedJob = await api.getJob(parseInt(jobId));
        setJob(fetchedJob);
        
        // Check if job is completed
        if (fetchedJob.status !== 'completed') {
          navigate(`/status/${jobId}`);
          return;
        }
        
        // Get result URL
        fetchResult();
        
      } catch (err) {
        setError('Nie udało się pobrać informacji o zadaniu.');
        toast({
          title: 'Błąd',
          description: 'Wystąpił problem podczas pobierania informacji o zadaniu.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchJob();
  }, [jobId]);

  const fetchResult = async () => {
    if (!jobId) return;
    
    setResultLoading(true);
    
    try {
      const jobResult = await api.getJobResult(parseInt(jobId));
      setResult(jobResult);
    } catch (err) {
      setError('Nie udało się pobrać linku do wyniku.');
      toast({
        title: 'Błąd',
        description: 'Wystąpił problem podczas pobierania linku do wyniku.',
        variant: 'destructive',
      });
    } finally {
      setResultLoading(false);
    }
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  const handleGoToHome = () => {
    navigate('/');
  };

  const handleDownload = () => {
    if (result?.url) {
      // Create a download link
      const link = document.createElement('a');
      link.href = result.url;
      link.download = `animated-${job?.original_filename.replace(/\.(jpg|jpeg|png)$/i, '')}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        title: 'Pobieranie rozpoczęte',
        description: 'Twój animowany film jest pobierany.',
      });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-xl mx-auto text-center space-y-4">
        <h1 className="text-2xl font-bold">Nie znaleziono wyniku</h1>
        <p className="text-muted-foreground">{error || 'Zadanie nie istnieje lub nie zostało ukończone.'}</p>
        <Button onClick={handleGoToHome}>Wróć do strony głównej</Button>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Pobierz animację</h1>
          <p className="text-muted-foreground">
            Twój szkic został przetworzony. Możesz teraz pobrać animowany film.
          </p>
        </div>

        <div className="border rounded-lg p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{job.original_filename}</p>
              <p className="text-sm text-muted-foreground">
                Ukończono: {formatDate(job.updated_at)}
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-green-500">
                <FileVideo className="h-5 w-5" />
                <span>MP4 1080p 30fps</span>
              </div>
              <p className="text-sm text-muted-foreground">ID: {job.id}</p>
            </div>
          </div>
          
          <div className="bg-muted p-6 rounded-md flex flex-col items-center justify-center">
            <div className="bg-background rounded-full p-6 mb-4">
              <FileVideo className="h-16 w-16 text-primary" />
            </div>
            <p className="font-medium mb-1">Animowany film jest gotowy do pobrania</p>
            <p className="text-sm text-muted-foreground mb-6">
              Format: MP4, Rozdzielczość: 1080p, FPS: 30
            </p>
            
            <Button 
              size="lg"
              onClick={handleDownload}
              disabled={resultLoading || !result}
              className="w-full max-w-xs"
            >
              {resultLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Przygotowywanie...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Pobierz film
                </>
              )}
            </Button>
          </div>
          
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={handleGoBack}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Wróć
            </Button>
            
            <Button
              variant="secondary"
              onClick={handleGoToHome}
            >
              Strona główna
            </Button>
          </div>
        </div>

        <div className="text-sm text-muted-foreground p-4 bg-muted rounded-md">
          <p>
            Pobrane filmy można wykorzystać w celach edukacyjnych, prezentacjach lub w mediach społecznościowych.
            Link do pobrania wygasa po 24 godzinach.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DownloadPage;
