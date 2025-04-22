import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Pencil, Upload, Clock, Download } from 'lucide-react'

const HomePage = () => {
  const navigate = useNavigate()

  return (
    <div className="max-w-4xl mx-auto">
      <div className="space-y-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight">
          Konwertuj szkice na animowane filmy
        </h1>
        <p className="text-xl text-muted-foreground">
          Zamień statyczne szkice JPG/PNG w dynamiczne animacje MP4/WEBM przedstawiające proces rysowania
        </p>
        
        <div className="flex justify-center py-4">
          <Button size="lg" onClick={() => navigate('/upload')}>
            Rozpocznij teraz
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-12">
        <div className="bg-card p-6 rounded-lg shadow-sm border">
          <div className="mb-4 flex items-center justify-center">
            <div className="p-3 rounded-full bg-primary/10">
              <Upload className="h-6 w-6 text-primary" />
            </div>
          </div>
          <h3 className="text-lg font-medium text-center mb-2">Krok 1: Upload</h3>
          <p className="text-sm text-muted-foreground text-center">
            Prześlij plik JPG lub PNG ze swoim szkicem. Maksymalny rozmiar pliku to 10 MB.
          </p>
        </div>
        
        <div className="bg-card p-6 rounded-lg shadow-sm border">
          <div className="mb-4 flex items-center justify-center">
            <div className="p-3 rounded-full bg-primary/10">
              <Clock className="h-6 w-6 text-primary" />
            </div>
          </div>
          <h3 className="text-lg font-medium text-center mb-2">Krok 2: Przetwarzanie</h3>
          <p className="text-sm text-muted-foreground text-center">
            Nasz system automatycznie przetworzy Twój szkic, wektoryzując go i dodając animację ręki.
          </p>
        </div>
        
        <div className="bg-card p-6 rounded-lg shadow-sm border">
          <div className="mb-4 flex items-center justify-center">
            <div className="p-3 rounded-full bg-primary/10">
              <Download className="h-6 w-6 text-primary" />
            </div>
          </div>
          <h3 className="text-lg font-medium text-center mb-2">Krok 3: Pobieranie</h3>
          <p className="text-sm text-muted-foreground text-center">
            Pobierz gotowy film MP4/WEBM w jakości 1080p 30fps przedstawiający proces rysowania.
          </p>
        </div>
      </div>
      
      <div className="mt-6 p-6 bg-muted rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Możliwości</h2>
        <ul className="space-y-2">
          <li className="flex items-start">
            <Pencil className="h-5 w-5 mr-2 text-primary mt-0.5" />
            <span>Automatyczna wektoryzacja szkiców i rysunków</span>
          </li>
          <li className="flex items-start">
            <Pencil className="h-5 w-5 mr-2 text-primary mt-0.5" />
            <span>Animacja procesu rysowania linii</span>
          </li>
          <li className="flex items-start">
            <Pencil className="h-5 w-5 mr-2 text-primary mt-0.5" />
            <span>Animowana ręka rysująca kontury</span>
          </li>
          <li className="flex items-start">
            <Pencil className="h-5 w-5 mr-2 text-primary mt-0.5" />
            <span>Film w wysokiej jakości 1080p 30fps</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default HomePage
