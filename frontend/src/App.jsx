import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ScrollToTop from './components/ScrollToTop'
import Home from './pages/Home'
import Movies from './pages/Movies'
import TvShows from './pages/TvShows'
import Anime from './pages/Anime'
import KDrama from './pages/KDrama'
import Search from './pages/Search'
import MovieDetail from './pages/MovieDetail'
import TvDetail from './pages/TvDetail'
import Watch from './pages/Watch'

export default function App() {
  return (
    <div className="min-h-screen bg-[#141414] text-white">
      <ScrollToTop />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/movies" element={<Movies />} />
        <Route path="/tv" element={<TvShows />} />
        <Route path="/anime" element={<Anime />} />
        <Route path="/kdrama" element={<KDrama />} />
        <Route path="/search" element={<Search />} />
        <Route path="/movie/:id" element={<MovieDetail />} />
        <Route path="/tv/:id" element={<TvDetail />} />
        <Route path="/watch/movie/:id" element={<Watch />} />
        <Route path="/watch/tv/:id/:season/:episode" element={<Watch />} />
        <Route path="/watch/anime/:id" element={<Watch />} />
        <Route path="/watch/drama/:id" element={<Watch />} />
      </Routes>
      <Footer />
    </div>
  )
}
