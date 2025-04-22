import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileType, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import { api } from '@/services/api';
import { formatFileSize } from '@/lib/utils';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const UploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { toast } = useToast();
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      
      // Validate file size
      if (selectedFile.size > MAX_FILE_SIZE) {
        toast({
          title: 'Błąd',
          description: `Plik jest zbyt duży. Maksymalny rozmiar to ${formatFileSize(MAX_FILE_SIZE)}.`,
          variant: 'destructive',
        });
        return;
      }

      // Validate file type
      if (!['image/jpeg', 'image/png'].includes(selectedFile.type)) {
        toast({
          title: 'Błąd',
          description: 'Dozwolone są tylko pliki JPG i PNG.',
          variant: 'destructive',
        });
        return;
      }

      setFile(selectedFile);
    }
  }, [toast]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
  });

  const uploadFile = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setUploadProgress(0);
    
    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const newProgress = prev + Math.random() * 10;
          return newProgress > 90 ? 90 : newProgress;
        });
      }, 300);
      
      // Upload the file
      const job = await api.uploadSketch(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      toast({
        title: 'Sukces',
        description: 'Plik został pomyślnie przesłany. Trwa przetwarzanie...',
      });
      
      // Navigate to status page
      setTimeout(() => {
        navigate(`/status/${job.id}`);
      }, 1000);
      
    } catch (error) {
      toast({
        title: 'Błąd',
        description: 'Wystąpił problem podczas przesyłania pliku. Spróbuj ponownie.',
        variant: 'destructive',
      });
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Prześlij szkic</h1>
          <p className="text-muted-foreground">
            Wybierz plik JPG lub PNG ze swoim szkicem, aby rozpocząć konwersję na animowany film.
          </p>
        </div>

        {!file ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
              isDragActive 
                ? 'border-primary bg-primary/5' 
                : 'border-muted-foreground/25 hover:border-primary/50'
            }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center gap-4">
              <div className="p-6 rounded-full bg-muted">
                <Upload className="h-10 w-10 text-muted-foreground" />
              </div>
              <div className="space-y-2">
                <p className="font-medium">
                  {isDragActive 
                    ? 'Upuść plik tutaj...' 
                    : 'Przeciągnij i upuść plik tutaj lub kliknij, aby wybrać'
                  }
                </p>
                <p className="text-sm text-muted-foreground">
                  Obsługiwane formaty: JPG, PNG (max. 10MB)
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="border rounded-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-md bg-muted">
                  <FileType className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
                </div>
              </div>
              {!isUploading && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRemoveFile}
                  disabled={isUploading}
                >
                  Usuń
                </Button>
              )}
            </div>
            
            {isUploading && (
              <div className="space-y-2">
                <Progress value={uploadProgress} />
                <p className="text-sm text-center text-muted-foreground">
                  Przesyłanie... {uploadProgress.toFixed(0)}%
                </p>
              </div>
            )}
            
            {!isUploading && (
              <div className="flex justify-end">
                <Button onClick={uploadFile}>
                  Prześlij i konwertuj
                </Button>
              </div>
            )}
          </div>
        )}
        
        <div className="bg-muted p-4 rounded-md flex gap-2">
          <AlertCircle className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
          <div className="text-sm text-muted-foreground">
            <p>
              Przetworzenie Twojego szkicu może potrwać do 90 sekund. Po przesłaniu będziesz mógł śledzić postęp konwersji.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
