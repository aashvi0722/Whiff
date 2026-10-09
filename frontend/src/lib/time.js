export function fmtHour(h, lang) {
  const hh = ((h % 24) + 24) % 24
  const h12 = hh % 12 === 0 ? 12 : hh % 12
  if (lang === 'hi') {
    const p = hh >= 4 && hh < 12 ? 'सुबह' : hh >= 12 && hh < 16 ? 'दोपहर' : hh >= 16 && hh < 19 ? 'शाम' : 'रात'
    return `${p} ${h12} बजे`
  }
  return `${h12} ${hh < 12 ? 'AM' : 'PM'}`
}
// start_h and end_h are inclusive hour slots: 6 to 8 means 6:00 to 9:00
export const fmtRange = (s, e, lang) => `${fmtHour(s, lang)} – ${fmtHour(e + 1, lang)}`