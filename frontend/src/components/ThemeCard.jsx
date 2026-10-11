import { useEffect, useRef, useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { useTheme } from '../theme/useTheme.jsx'

const ICON = {
  auto: <><circle cx="12" cy="12" r="8.5" /><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor" /></>,
  light: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></>,
  dark: <path d="M21 13.5A8.5 8.5 0 1 1 10.5 3a7 7 0 0 0 10.5 10.5z" />,
}
const MODES = ['auto', 'light', 'dark']
const Svg = ({ children, cls }) => (
  <svg className={'ni ' + (cls || '')} viewBox="0 0 24 24" aria-hidden="true">{children}</svg>
)

export default function ThemeCard() {
  const { t } = useLang()
  const { mode, setMode } = useTheme()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    const away = e => { if (!ref.current?.contains(e.target)) setOpen(false) }
    const esc = e => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', away)
    document.addEventListener('keydown', esc)
    return () => { document.removeEventListener('mousedown', away); document.removeEventListener('keydown', esc) }
  }, [open])

  useEffect(() => {
  if (!open) return
  const id = setTimeout(
    () => ref.current?.querySelector('.dd-list')?.scrollIntoView({ block: 'nearest', behavior: 'smooth' }), 60)
  return () => clearTimeout(id)
}, [open])

  const pick = m => { setMode(m); setOpen(false) }

  return (
    <section className="glass-card stack" style={{ gap: 8, position: 'relative', zIndex: open ? 20 : 1 }}>
      <span className="eyebrow" id="theme-lbl">{t('theme')}</span>
      <div className="dd" ref={ref}>
        <button type="button" className="dd-btn" aria-haspopup="listbox" aria-expanded={open}
                aria-labelledby="theme-lbl" onClick={() => setOpen(o => !o)}>
          <span className="dd-ic"><Svg>{ICON[mode]}</Svg></span>
          <span className="dd-val">{t('theme_' + mode)}</span>
          <Svg cls={'dd-chev' + (open ? ' up' : '')}><path d="M6 9l6 6 6-6" /></Svg>
        </button>
        {open && (
          <ul className="dd-list" role="listbox" aria-labelledby="theme-lbl">
            {MODES.map(m => (
              <li key={m} role="option" aria-selected={mode === m} tabIndex={0}
                  className={'dd-opt' + (mode === m ? ' on' : '')}
                  onClick={() => pick(m)}
                  onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(m) } }}>
                <span className="dd-ic"><Svg>{ICON[m]}</Svg></span>
                <span className="tx"><strong>{t('theme_' + m)}</strong><small>{t('theme_' + m + '_d')}</small></span>
                <Svg cls="dd-check"><path d="M5 12l5 5 9-10" /></Svg>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}