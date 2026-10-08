import { NavLink, Route, Routes } from 'react-router-dom'
import Radar from './screens/Radar.jsx'
import Day from './screens/Day.jsx'
import Profile from './screens/Profile.jsx'

export default function App() {
  return (
    <div className="app">
      <main className="screen">
        <Routes>
          <Route path="/" element={<Radar />} />
          <Route path="/day" element={<Day />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
      <nav className="nav">
        <NavLink to="/" end>Radar</NavLink>
        <NavLink to="/day">Plan</NavLink>
        <NavLink to="/profile">Me</NavLink>
      </nav>
    </div>
  )
}