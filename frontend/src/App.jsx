import { ThemeProvider, useTheme } from './theme/useTheme.jsx'
import { NavLink, Route, Routes } from 'react-router-dom'
import { LangProvider, useLang } from './i18n/useLang.jsx'
import Radar from './screens/Radar.jsx'
import Day from './screens/Day.jsx'
import Profile from './screens/Profile.jsx'

const Icon = ({ children }) => <svg className="ni" viewBox="0 0 24 24" aria-hidden="true">{children}</svg>
const RadarIcon = () => <Icon><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="4.5" /><path d="M12 12l6-6" /></Icon>
const PlanIcon = () => <Icon><rect x="3.5" y="5" width="17" height="15" rx="3" /><path d="M3.5 10h17M8 3v4M16 3v4" /></Icon>
const MeIcon = () => <Icon><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></Icon>

function ThemeButton() {
  const { mode, cycle } = useTheme()
  const { t } = useLang()
  const label = `${t('theme')}: ${t('theme_' + mode)}`
  return (
    <button className="iconbtn" onClick={cycle} aria-label={label} title={label}>
      <svg className="ni" viewBox="0 0 24 24" aria-hidden="true">
        {mode === 'light' && <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>}
        {mode === 'dark' && <path d="M21 13.5A8.5 8.5 0 1 1 10.5 3a7 7 0 0 0 10.5 10.5z" />}
        {mode === 'auto' && <><circle cx="12" cy="12" r="8.5" /><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor" /></>}
      </svg>
    </button>
  )
}

function TopBar() {
  const { lang, setLang } = useLang()
  return (
    <header className="topbar">
      <div className="brand">
        <span className="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M3 8h11a3 3 0 1 0-3-3" /><path d="M3 12h16a3 3 0 1 1-3 3" /><path d="M3 16h8" />
          </svg>
        </span>
        <span className="brand-name">Whiff</span>
      </div>
      <div className="row">
  <ThemeButton />
  <div className="seg" role="group" aria-label="Language">
    <button className={lang === 'en' ? 'on' : ''} aria-pressed={lang === 'en'} onClick={() => setLang('en')}>EN</button>
    <button className={lang === 'hi' ? 'on' : ''} aria-pressed={lang === 'hi'} onClick={() => setLang('hi')}>हिं</button>
  </div>
</div>
    </header>
  )
}

function Shell() {
  const { t } = useLang()
  return (
    <div className="app">
      <TopBar />
      <main className="screen">
        <Routes>
          <Route path="/" element={<Radar />} />
          <Route path="/day" element={<Day />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
      <nav className="nav" aria-label="Main">
        <NavLink to="/" end><RadarIcon /><span>{t('nav_radar')}</span></NavLink>
        <NavLink to="/day"><PlanIcon /><span>{t('nav_plan')}</span></NavLink>
        <NavLink to="/profile"><MeIcon /><span>{t('nav_me')}</span></NavLink>
      </nav>
    </div>
  )
}

export default function App() {
  return <LangProvider><ThemeProvider><Shell /></ThemeProvider></LangProvider>
}