import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'

const NotFoundPage = () => {
  const navigate = useNavigate()

  return (
    <div className="max-w-md mx-auto text-center py-10 space-y-6">
      <h1 className="text-9xl font-bold text-primary">404</h1>
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Strona nie znaleziona</h2>
        <p className="text-muted-foreground">
          Przepraszamy, strona której szukasz nie istnieje lub została przeniesiona.
        </p>
      </div>
      <div className="pt-4">
        <Button onClick={() => navigate('/')}>
          Wróć do strony głównej
        </Button>
      </div>
    </div>
  )
}

export default NotFoundPage
