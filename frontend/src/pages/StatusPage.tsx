import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, Clock, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import { api, Job } from '@/services/api';
import { formatDate } from '@/lib/utils';

const StatusPage = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Fetch job status
  const fetchJobStatus = async () => {
    if (!jobId) return;
    
    try {
      const fetchedJob = await api.getJob(parseInt(jobId));
      setJob(fetchedJob);
      setError(null);
      
      // Calculate progress based on status
      switch (fetchedJob.status) {
        case 'pending':
          setProgress(10);
          break;
        case 'processing':
          setProgress(50);
          break;
        case 'completed':
          setProgress(100);
          break;
        case 'failed':
          setProgress(0);
          break;
      }
      
    } catch (err) {
      setError('Nie udało się pobrać informacji o zadaniu.');
      toast({
        title: 'Błąd',
        description: 'Wystąpił problem podczas pobierania statusu zadania.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobStatus();
    
    // Poll for updates if job is pending or processing
    const interval = setInterval(() => {
      if (job && (job.status === 'pending' || job.status === 'processing')) {
        fetchJobStatus();
      }
    }, 5000); // Poll every 5 seconds
    
    return () => clearInterval(interval);
  }, [jobId, job?.status]);

  const handleRefresh = () => {
    setLoading(true);
    fetchJobStatus();
  };

  const handleGoToDownload = () => {
    if (job && job.status === 'completed') {
      navigate(`/download/${job.id}`);
    }
  };

  const handleGoToUpload = () => {
    navigate('/upload');
  };

  // Status indicators
  const renderStatusIndicator = () => {
    if (!job) return null;
    
    switch (job.status) {
      case 'pending':
        return (
          <div className="flex items-center gap-2 text-amber-500">
            <Clock className="h-5 w-5" />
            <span>Oczekiwanie</span>
          </div>
        );
      case 'processing':
        return (
          <div className="flex items-center gap-2 text-blue-500">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Przetwarzanie</span>
          </div>
        );
      case 'completed':
        return (
          <div className="flex items-center gap-2 text-green-500">
            <CheckCircle className="h-5 w-5" />
            <span>Ukończono</span>
          </div>
        );
      case 'failed':
        return (
          <div className="flex items-center gap-2 text-red-500">
            <XCircle className="h-5 w-5" />
            <span>Błąd</span>
          </div>
        );
      default:
        return null;
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
        <h1 className="text-2xl font-bold">Nie znaleziono zadania</h1>
        <p className="text-muted-foreground">{error || 'Zadanie nie istnieje lub zostało usunięte.'}</p>
        <Button onClick={handleGoToUpload}>Prześlij nowy szkic</Button>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Status przetwarzania</h1>
          <p className="text-muted-foreground">
            Poniżej znajdziesz informacje o postępie przetwarzania Twojego szkicu.
          </p>
        </div>

        <div className="border rounded-lg p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{job.original_filename}</p>
              <p className="text-sm text-muted-foreground">
                Przesłano: {formatDate(job.created_at)}
              </p>
            </div>
            <div className="text-right">
              <div>{renderStatusIndicator()}</div>
              <p className="text-sm text-muted-foreground">ID: {job.id}</p>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Postęp</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>
          
          {job.error_message && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-md text-red-800 text-sm">
              <p className="font-medium">Wystąpił błąd:</p>
              <p>{job.error_message}</p>
            </div>
          )}
          
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={loading}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Odśwież
            </Button>
            
            {job.status === 'completed' ? (
              <Button onClick={handleGoToDownload}>
                Pobierz rezultat
              </Button>
            ) : (
              <Button
                variant="secondary"
                onClick={handleGoToUpload}
              >
                Prześlij nowy szkic
              </Button>
            )}
          </div>
        </div>

        <div className="text-sm text-muted-foreground p-4 bg-muted rounded-md">
          <p>
            {job.status === 'pending' && 'Twój szkic czeka na przetworzenie. To nie powinno potrwać długo...'}
            {job.status === 'processing' && 'Twój szkic jest właśnie przetwarzany. Ten proces może potrwać do 90 sekund.'}
            {job.status === 'completed' && 'Twój animowany film jest gotowy! Możesz go teraz pobrać.'}
            {job.status === 'failed' && 'Niestety, przetwarzanie nie powiodło się. Możesz spróbować ponownie przesłać plik.'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default StatusPage;
