import { useEffect } from 'react'
import { useRouter } from './router'
import { Header } from './components/Header'
import { GalleryView } from './views/GalleryView'
import { MethodView } from './views/MethodView'
import { CompareView } from './views/CompareView'
import { DocsView } from './views/DocsView'
import { useMethods } from './data/useMethods'
import { navigateTo } from './router'

export default function App() {
  const [route] = useRouter()
  const { meta, methods, byId } = useMethods()

  // Handle the filter-category custom event dispatched from MethodView breadcrumb
  useEffect(() => {
    const handler = (e: Event) => {
      const cat = (e as CustomEvent).detail as string
      // Store the category in sessionStorage so GalleryView can pick it up
      sessionStorage.setItem('qgallery:jump-category', cat)
    }
    window.addEventListener('filter-category', handler)
    return () => window.removeEventListener('filter-category', handler)
  }, [])

  // Scroll to top on route change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [route])

  const renderView = () => {
    switch (route.view) {
      case 'gallery':
        return <GalleryView />
      case 'method':
        return <MethodView id={route.id} />
      case 'compare':
        return <CompareView ids={route.ids} />
      case 'docs':
        return <DocsView page={route.page} />
      default:
        return <GalleryView />
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-gray-950">
      <Header count={meta.count} />
      <div className="flex-1">
        {renderView()}
      </div>
    </div>
  )
}
