import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { t as translate, tryT as tryTranslate, cityName, regionName } from './index.js'

const Ctx = createContext(null)
const KEY = 'whiff_lang'

function initialLang() {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved === 'en' || saved === 'hi') return saved
  } catch {}
  return (navigator.language || '').toLowerCase().startsWith('hi') ? 'hi' : 'en'
}

export function LangProvider({ children }) {
  const [lang, setLangState] = useState(initialLang)
  useEffect(() => { document.documentElement.lang = lang }, [lang])
  const setLang = useCallback(l => {
    setLangState(l)
    try { localStorage.setItem(KEY, l) } catch {}
  }, [])
   const value = useMemo(() => ({
    lang, setLang,
    t: (code, params) => translate(code, lang, params),
    tryT: (code, params) => tryTranslate(code, lang, params),
    city: label => cityName(label, lang),
    region: code => regionName(code, lang),
  }), [lang, setLang])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useLang() {
  const v = useContext(Ctx)
  if (!v) throw new Error('useLang must be used inside <LangProvider>')
  return v
}