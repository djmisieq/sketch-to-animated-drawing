import { NavLink } from 'react-router-dom'
import { Pencil } from 'lucide-react'
import { Button } from '@/components/ui/button'

const Header = () => {
  return (
    <header className="bg-primary text-primary-foreground py-4 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Pencil className="h-6 w-6" />
          <span className="text-xl font-bold">Sketch-to-Animated-Drawing</span>
        </div>
        
        <nav>
          <ul className="flex space-x-6">
            <li>
              <NavLink 
                to="/" 
                className={({ isActive }) => 
                  isActive ? "font-bold underline" : "hover:underline"
                }
                end
              >
                Strona główna
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/upload" 
                className={({ isActive }) => 
                  isActive ? "font-bold underline" : "hover:underline"
                }
              >
                Upload
              </NavLink>
            </li>
          </ul>
        </nav>
        
        <Button asChild variant="secondary">
          <NavLink to="/upload">
            Dodaj nowy szkic
          </NavLink>
        </Button>
      </div>
    </header>
  )
}

export default Header
