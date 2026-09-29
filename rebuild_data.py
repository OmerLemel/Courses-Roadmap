import json, re, sys, itertools
sys.stdout.reconfigure(encoding='utf-8')

def ctype(rama_name):
    n = rama_name or ''
    if 'שאר רוח' in n: return 'שאר רוח'
    if 'סמינר' in n: return 'סמינר'
    if 'סדנה' in n or 'סדנא' in n: return 'סדנה'
    if 'ליבה' in n: return 'ליבה'
    if 'ייעוד' in n: return 'ליבה'
    if 'מעבד' in n or 'פרויקט' in n: return 'חובה'  # labs / final projects are required
    if 'חובה' in n: return 'חובה'
    if 'בחירה' in n: return 'בחירה'
    return None

def year_info(top, sub):
    y = 0; sem = ''
    if 'א\'' in top or top.strip() == "שנה א'" or 'שנה א' in top: y = 1
    elif 'שנה ב' in top: y = 2
    elif 'שנה ג' in top: y = 3
    elif 'שנים ב' in top: y = 0
    elif 'שנה ד' in top: y = 4
    elif 'שנה ה' in top: y = 5
    if 'שאר רוח' in top: y = 6
    if "סמסטר א" in sub: sem = 'א'
    elif "סמסטר ב" in sub: sem = 'ב'
    return y, sem

PROG_DEFAULT = {'t7225': 'חובה', 't7844': 'חובה', 't7974': 'חובה'}
              # unmarked sections in these programs are required

programs = {
  "dual": {"id": "dual", "school": "math", "tcids": {'2025': ['7612'], '2026': ['7612']},
           "name": "מתמטיקה ומדעי המחשב (דו-חוגי)",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7612", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7612"},
  "csai": {"id": "csai", "school": "cs", "tcids": {'2026': ['8865']},
           "name": "מדעי המחשב עם חטיבת בינה מלאכותית",
           "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8865"},
  "math": {"id": "math", "school": "math", "tcids": {'2025': ['7606'], '2026': ['7606']},
           "name": "מתמטיקה עיונית (חד-חוגי)",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7606", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7606"},
  "cs": {"id": "cs", "school": "cs", "tcids": {'2025': ['7583'], '2026': ['7583']},
           "name": "מדעי המחשב (חד-חוגי)",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7583", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7583"},
  "t7605": {"id": "t7605", "school": "math", "tcids": {"2025": ["7605"], "2026": ["7605"]},
           "name": "תוכנית חד-חוגית במתמטיקה במגמת מתמטיקה שימושית",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7605", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7605"},
  "t8650": {"id": "t8650", "school": "math", "tcids": {"2025": ["8650"], "2026": ["8650"]},
           "name": "תוכנית חד-חוגית במתמטיקה במגמת מדעי המחשב",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8650", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8650"},
  "t8359": {"id": "t8359", "school": "math", "tcids": {"2025": ["8359"], "2026": ["8359"]},
           "name": "תוכנית חד-חוגית במתמטיקה במגמת חקר ביצועים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8359", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8359"},
  "t8360": {"id": "t8360", "school": "math", "tcids": {"2025": ["8360"], "2026": ["8360"]},
           "name": "תוכנית חד-חוגית במתמטיקה במגמת סטטיסטיקה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8360", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8360"},
  "t7640": {"id": "t7640", "school": "math", "tcids": {"2025": ["7640"], "2026": ["7640"]},
           "name": "תוכנית חד-חוגית במתמטיקה בשילוב קורסים במדעי הרוח",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7640", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7640"},
  "t8770": {"id": "t8770", "school": "math", "tcids": {"2025": ["8770"], "2026": ["8770"]},
           "name": "תוכנית דו-חוגית במתמטיקה ובסטטיסטיקה ומדע הנתונים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8770", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8770"},
  "t7820": {"id": "t7820", "school": "math", "tcids": {"2025": ["7820"], "2026": ["7820"]},
           "name": "תוכנית דו-חוגית במתמטיקה ובסטטיסטיקה ומדע הנתונים במסלול מתמטיקה שימושית וסטטיסטיקה להייטק",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7820", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7820"},
  "t7611": {"id": "t7611", "school": "math", "tcids": {"2025": ["7611"], "2026": ["7611"]},
           "name": "תוכנית דו-חוגית במתמטיקה ובכימיה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7611", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7611"},
  "t7610": {"id": "t7610", "school": "math", "tcids": {"2025": ["7610"], "2026": ["7610"]},
           "name": "תוכנית דו-חוגית במתמטיקה ובמדעי כדור הארץ",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7610", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7610"},
  "t7618": {"id": "t7618", "school": "math", "tcids": {"2025": ["7618"], "2026": ["7618"]},
           "name": "תוכנית דו-חוגית במתמטיקה ובחוג נוסף",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7618", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7618"},
  "t8614": {"id": "t8614", "school": "stats", "tcids": {"2025": ["8614"], "2026": ["8614"]},
           "name": "תוכנית חד-חוגית בסטטיסטיקה ומדע הנתונים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8614", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8614"},
  "t8390": {"id": "t8390", "school": "stats", "tcids": {"2025": ["8390"], "2026": ["8390"]},
           "name": "תוכנית חד-חוגית במדעי הנתונים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8390", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8390"},
  "t8620": {"id": "t8620", "school": "stats", "tcids": {"2025": ["8620"], "2026": ["8620"]},
           "name": "תוכנית דו-חוגית בסטטיסטיקה ומדע הנתונים ובמדעי המחשב",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8620", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8620"},
  "t8617": {"id": "t8617", "school": "stats", "tcids": {"2025": ["8617"], "2026": ["8617"]},
           "name": "תוכנית דו-חוגית בסטטיסטיקה ומדע הנתונים ובחוג נוסף",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8617", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8617"},
  "t8032": {"id": "t8032", "school": "cs", "tcids": {"2025": ["8032"], "2026": ["8032"]},
           "name": "תוכנית  חד חוגית במדעי המחשב בשילוב קורסים במדעי  הרוח",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8032", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8032"},
  "t8047": {"id": "t8047", "school": "cs", "tcids": {"2025": ["8047"], "2026": ["8047"]},
           "name": "תכנית חד-חוגית במדעי המחשב עם חטיבה ביזמות",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8047", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8047"},
  "t8366": {"id": "t8366", "school": "physics", "tcids": {"2025": ["8366"], "2026": ["8366"]},
           "name": "תוכנית חד-חוגית בפיזיקה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8366", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8366"},
  "t8376": {"id": "t8376", "school": "physics", "tcids": {"2025": ["8376"], "2026": ["8376"]},
           "name": "תוכנית חד-חוגית בפיזיקה עם חטיבה במדעי המוח",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8376", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8376"},
  "t8367": {"id": "t8367", "school": "physics", "tcids": {"2025": ["8367"], "2026": ["8367"]},
           "name": "תוכנית חד-חוגית בפיזיקה עם חטיבה במדעי החיים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8367", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8367"},
  "t8365": {"id": "t8365", "school": "physics", "tcids": {"2025": ["8365"], "2026": ["8365"]},
           "name": "תוכנית לימודים חד חוגית בפיזיקה בשילוב קורסים במדעי הרוח",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8365", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8365"},
  "t8358": {"id": "t8358", "school": "physics", "tcids": {"2025": ["8358"], "2026": ["8358"]},
           "name": "תוכנית דו-חוגית בפיזיקה  ובחוג נוסף",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8358", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8358"},
  "t8368": {"id": "t8368", "school": "physics", "tcids": {"2025": ["8368"], "2026": ["8368"]},
           "name": "תוכנית דו-חוגית בפיזיקה ובמדעי כדור הארץ",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8368", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8368"},
  "t8371": {"id": "t8371", "school": "physics", "tcids": {"2025": ["8371"], "2026": ["8371"]},
           "name": "תוכנית  משולבת בפיזיקה ובמתמטיקה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8371", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8371"},
  "t8369": {"id": "t8369", "school": "physics", "tcids": {"2025": ["8369"], "2026": ["8369"]},
           "name": "תוכנית דו-חוגית בפיזיקה ובמדעי המחשב",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8369", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8369"},
  "t8370": {"id": "t8370", "school": "physics", "tcids": {"2025": ["8370"], "2026": ["8370"]},
           "name": "תוכנית דו-חוגית בפיזיקה ובמדעי המחשב במסלול מחשוב קוונטי",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8370", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8370"},
  "t7600": {"id": "t7600", "school": "chem", "tcids": {"2025": ["7600"], "2026": ["7600"]},
           "name": "תוכנית חד-חוגית בכימיה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7600", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7600"},
  "t7601": {"id": "t7601", "school": "chem", "tcids": {"2025": ["7601"], "2026": ["7601"]},
           "name": "תוכנית חד-חוגית בכימיה - התוכנית המחקרית לתלמידים מצטיינים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7601", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7601"},
  "t7657": {"id": "t7657", "school": "chem", "tcids": {"2025": ["7657"], "2026": ["7657"]},
           "name": "תוכנית חד-חוגית בכימיה בשילוב קורסים במדעי הרוח",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7657", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7657"},
  "t6387": {"id": "t6387", "school": "chem", "tcids": {"2025": ["6387"], "2026": ["6387"]},
           "name": "תוכנית דו-חוגית בכימיה ובחוג נוסף",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=6387", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=6387"},
  "t7604": {"id": "t7604", "school": "chem", "tcids": {"2025": ["7604"], "2026": ["7604"]},
           "name": "תוכנית דו-חוגית בכימיה ובמדעי המחשב",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7604", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7604"},
  "t7818": {"id": "t7818", "school": "chem", "tcids": {"2025": ["7818"], "2026": ["7818"]},
           "name": "תוכנית דו-חוגית בכימיה ובפיזיקה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7818", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7818"},
  "t7588": {"id": "t7588", "school": "earth", "tcids": {"2025": ["7588"], "2026": ["7588"]},
           "name": "תוכנית חד-חוגית במדעי כדור הארץ",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7588", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7588"},
  "t7589": {"id": "t7589", "school": "earth", "tcids": {"2025": ["7589"], "2026": ["7589"]},
           "name": "תוכנית חד-חוגית במדעי כדור הארץ - התוכנית המחקרית לתלמידים מצטיינים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7589", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7589"},
  "t8185": {"id": "t8185", "school": "earth", "tcids": {"2025": ["8185"], "2026": ["8185"]},
           "name": "תכנית לימודים חד-חוגית במדעי כדור הארץ עם חטיבה בבינה מלאכותית ובמדעי הנתונים",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=8185", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8185"},
  "t7590": {"id": "t7590", "school": "earth", "tcids": {"2025": ["7590"], "2026": ["7590"]},
           "name": "תוכנית דו-חוגית במדעי כדור הארץ ובחוג נוסף",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7590", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7590"},
  "t7593": {"id": "t7593", "school": "earth", "tcids": {"2025": ["7593"], "2026": ["7593"]},
           "name": "תוכנית דו-חוגית במדעי כדור הארץ ובמדעי המחשב",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7593", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7593"},
  "t7225": {"id": "t7225", "school": "physics", "tcids": {"2025": ["7225"], "2026": ["7225"]},
           "name": "תוכנית משולבת בהנדסת חשמל ובפיזיקה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7225", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7225"},
  "t8996": {"id": "t8996", "school": "chem", "tcids": {"2026": ["8996"]},
           "name": "תוכנית דו-חוגית בכימיה ובביולוגיה",
           "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8996"},
  "t7844": {"id": "t7844", "school": "chem", "tcids": {"2025": ["7844"], "2026": ["7844"]},
           "name": "תואר כפול  במדע והנדסה של חומרים ובכימיה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7844", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7844"},
  "t7974": {"id": "t7974", "school": "earth", "tcids": {"2025": ["7974"], "2026": ["7974"]},
           "name": "תואר כפול בהנדסה מכנית ובמדעי כדור הארץ עם הדגש בלימודי סביבה",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7974", "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7974"},
}
filemap = {
  "cs_2025": "prog_7583_2025.json", "cs_2026": "prog_7583_2026.json", "csai_2026": "prog_8865_2026.json",
  "dual_2025": "prog_7612_2025.json", "dual_2026": "prog_7612_2026.json", "math_2025": "prog_7606_2025.json",
  "math_2026": "prog_7606_2026.json", "t6387_2025": "prog_6387_2025.json", "t6387_2026": "prog_6387_2026.json",
  "t7588_2025": "prog_7588_2025.json", "t7588_2026": "prog_7588_2026.json", "t7589_2025": "prog_7589_2025.json",
  "t7589_2026": "prog_7589_2026.json", "t7590_2025": "prog_7590_2025.json", "t7590_2026": "prog_7590_2026.json",
  "t7593_2025": "prog_7593_2025.json", "t7593_2026": "prog_7593_2026.json", "t7600_2025": "prog_7600_2025.json",
  "t7600_2026": "prog_7600_2026.json", "t7601_2025": "prog_7601_2025.json", "t7601_2026": "prog_7601_2026.json",
  "t7604_2025": "prog_7604_2025.json", "t7604_2026": "prog_7604_2026.json", "t7605_2025": "prog_7605_2025.json",
  "t7605_2026": "prog_7605_2026.json", "t7610_2025": "prog_7610_2025.json", "t7610_2026": "prog_7610_2026.json",
  "t7611_2025": "prog_7611_2025.json", "t7611_2026": "prog_7611_2026.json", "t7618_2025": "prog_7618_2025.json",
  "t7618_2026": "prog_7618_2026.json", "t7640_2025": "prog_7640_2025.json", "t7640_2026": "prog_7640_2026.json",
  "t7657_2025": "prog_7657_2025.json", "t7657_2026": "prog_7657_2026.json", "t7818_2025": "prog_7818_2025.json",
  "t7818_2026": "prog_7818_2026.json", "t7820_2025": "prog_7820_2025.json", "t7820_2026": "prog_7820_2026.json",
  "t8032_2025": "prog_8032_2025.json", "t8032_2026": "prog_8032_2026.json", "t8047_2025": "prog_8047_2025.json",
  "t8047_2026": "prog_8047_2026.json", "t8185_2025": "prog_8185_2025.json", "t8185_2026": "prog_8185_2026.json",
  "t8358_2025": "prog_8358_2025.json", "t8358_2026": "prog_8358_2026.json", "t8359_2025": "prog_8359_2025.json",
  "t8359_2026": "prog_8359_2026.json", "t8360_2025": "prog_8360_2025.json", "t8360_2026": "prog_8360_2026.json",
  "t8365_2025": "prog_8365_2025.json", "t8365_2026": "prog_8365_2026.json", "t8366_2025": "prog_8366_2025.json",
  "t8366_2026": "prog_8366_2026.json", "t8367_2025": "prog_8367_2025.json", "t8367_2026": "prog_8367_2026.json",
  "t8368_2025": "prog_8368_2025.json", "t8368_2026": "prog_8368_2026.json", "t8369_2025": "prog_8369_2025.json",
  "t8369_2026": "prog_8369_2026.json", "t8370_2025": "prog_8370_2025.json", "t8370_2026": "prog_8370_2026.json",
  "t8371_2025": "prog_8371_2025.json", "t8371_2026": "prog_8371_2026.json", "t8376_2025": "prog_8376_2025.json",
  "t8376_2026": "prog_8376_2026.json", "t8390_2025": "prog_8390_2025.json", "t8390_2026": "prog_8390_2026.json",
  "t8614_2025": "prog_8614_2025.json", "t8614_2026": "prog_8614_2026.json", "t8617_2025": "prog_8617_2025.json",
  "t8617_2026": "prog_8617_2026.json", "t8620_2025": "prog_8620_2025.json", "t8620_2026": "prog_8620_2026.json",
  "t8650_2025": "prog_8650_2025.json", "t8650_2026": "prog_8650_2026.json", "t8770_2025": "prog_8770_2025.json",
  "t8770_2026": "prog_8770_2026.json", "t7225_2025": "prog_7225_2025.json", "t7225_2026": "prog_7225_2026.json",
  "t8996_2026": "prog_8996_2026.json", "t7844_2025": "prog_7844_2025.json", "t7844_2026": "prog_7844_2026.json",
  "t7974_2025": "prog_7974_2025.json", "t7974_2026": "prog_7974_2026.json"
}
prereq = json.load(open('prereqs.json', encoding='utf-8'))

courses = {}
expected = {}  # (show, prog, year) -> raw-derived occ, for the audit below
multi = {}  # (show, prog, year) -> set of distinct derived tuples (cross-listings)
for key, fn in filemap.items():
    prog = key.rsplit('_', 1)[0]; year = key.rsplit('_', 1)[1]
    d = json.load(open(fn, encoding='utf-8'))
    def walk(rs, top='', sub=''):
        for r in rs:
            name = r.get('teurrama', '')
            for k in r.get('kurs', []) or []:
                show = k.get('kursshow', '').strip()
                if not show: continue
                if show in courses:  # prefer non-empty name/credits across occurrences
                    c = courses[show]
                    if not c['name'] and k.get('teurkurs'): c['name'] = k['teurkurs']
                    if not c['credits'] and k.get('shaotuni'): c['credits'] = k['shaotuni']
                else:
                    c = courses[show] = {"id": show, "kursid": k['kursid'], "name": k.get('teurkurs', ''),
                                         "credits": k.get('shaotuni', ''), "programs": {}, "occ": {}}
                c['programs'].setdefault(prog, {})
                t = ctype(name)
                if t is None: t = PROG_DEFAULT.get(prog, 'בחירה')
                y, sem = year_info(top or name, name)
                c['occ'][f'{prog}_{year}'] = {"type": t, "year": y, "sem": sem,
                                                   "rama": (top + ' / ' + name if top else name)}
                c['programs'][prog][year] = {"type": t, "year": y, "sem": sem,
                                             "rama": (top + ' / ' + name if top else name)}
                expected[(show, prog, year)] = dict(c['programs'][prog][year])
                multi.setdefault((show, prog, year), set()).add((t, y, sem))
            if r.get('rama'):
                walk(r['rama'], top or name, name)
    walk(d['rama'])

show_set = set(courses.keys())
edges = []
for kursid, v in prereq.items():
    tgt = v['show']
    if tgt not in show_set: continue
    for s in v.get('pre', []):
        if s in show_set: edges.append({"from": s, "to": tgt, "kind": "pre"})
    for s in v.get('par', []) or []:
        if s in show_set: edges.append({"from": s, "to": tgt, "kind": "co"})
seen = set(); ue = []
for e in edges:
    k = (e['from'], e['to'], e['kind'])
    if k not in seen: seen.add(k); ue.append(e)
edges = ue
for show, c in courses.items():
    ys = [o['year'] for o in c['occ'].values() if o['year'] in (1, 2, 3, 4, 5)]
    c['year'] = min(ys) if ys else 4

# --- manual semester overrides (teaching schedule beats yedion structure) ---
# Value form: "SEM" (all programs) or {"sem": "SEM", "programs": [...]} (scoped).
covered = set()
try:
    ovr = json.load(open('overrides.json', encoding='utf-8'))
    for show, rule in (ovr.get('sem') or {}).items():
        if isinstance(rule, dict):
            sem, progs = rule.get('sem', ''), rule.get('programs')
        else:
            sem, progs = rule, None
        if sem not in ('א', 'ב', ''):
            print('override: bad semester value for', show, repr(sem))
            continue
        c = courses.get(show)
        if not c:
            print('override: unknown course', show)
            continue
        targets = [p for p in (progs if progs is not None else list(c['programs']))]
        for p in targets:
            if p not in c['programs']:
                print('override: %s not present in program %s' % (show, p))
                continue
            for y in c['programs'][p]:
                c['programs'][p][y]['sem'] = sem
                covered.add((show, p, y))
        for key in list(c['occ']):
            p2 = key.rsplit('_', 1)[0]
            if progs is None or p2 in (progs or []):
                c['occ'][key]['sem'] = sem
    print('overrides applied, covered occurrences:', len(covered))
except FileNotFoundError:
    pass

# --- logic groups (או/וגם) ---
code_re = re.compile(r'\((\d{3,4}-\d{3,4})\)')
tag_re = re.compile(r'<[^>]+>')
ou_re = re.compile(r'(?:^|\s)או(?:\s|$)')
def clean(s):
    t = tag_re.sub('', s).replace('&nbsp;', ' ').strip()
    return re.sub(r'\s+', ' ', t)
def parse(raw_list):
    seq = []
    for s in raw_list or []:
        t = clean(s)
        if t == 'או': seq.append(('or',)); continue
        if t == '+': seq.append(('plus',)); continue
        ms = list(code_re.finditer(s))
        if not ms: continue
        bolds = [clean(b) for b in re.findall(r'<b>(.*?)</b>', s)]
        prev = 0
        for i, m in enumerate(ms):
            between = clean(s[prev:m.start()])
            if i > 0 and ou_re.search(between): seq.append(('or',))
            seq.append(('c', m.group(1), bolds[i] if i < len(bolds) else ''))
            prev = m.end()
    blocks, cur = [], []
    for it in seq:
        if it[0] == 'plus': blocks.append(cur); cur = []
        else: cur.append(it)
    blocks.append(cur)
    alt_lists = []
    for seg in blocks:
        alts, a = [], []
        for it in seg:
            if it[0] == 'or':
                if a: alts.append(a); a = []
            else: a.append((it[1], it[2]))
        if a: alts.append(a)
        if alts: alt_lists.append(alts)
    if not alt_lists: return [], {}
    names = {}
    for alts in alt_lists:
        for a in alts:
            for code, nm in a:
                if nm and code not in names: names[code] = nm
    groups = []
    for combo in itertools.product(*alt_lists):
        g = []
        for alt in combo: g.extend(alt)
        seen2, u = set(), []
        for code, nm in g:
            if code not in seen2: seen2.add(code); u.append(code)
        if u and u not in groups: groups.append(u)
    return groups, names

by_show = {c['id']: c for c in courses.values()}
ext = {}
for kursid, v in prereq.items():
    show = v.get('show')
    if show not in by_show: continue
    gpre, n1 = parse(v.get('raw_pre'))
    gco, n2 = parse(v.get('raw_par'))
    by_show[show]['reqPre'] = gpre
    by_show[show]['reqCo'] = gco
    for dd in (n1, n2):
        for k, nm in dd.items(): ext.setdefault(k, nm)
for c in courses.values():
    c.setdefault('reqPre', []); c.setdefault('reqCo', [])

# --- audit: final placements must equal raw-derived ones, except override-covered semesters ---
bad = 0
checked = 0
for c in courses.values():
    for p, ys in c['programs'].items():
        for y, o in ys.items():
            e = expected.get((c['id'], p, y))
            checked += 1
            if e is None:
                print('AUDIT missing expected occ for', c['id'], p, y)
                bad += 1
                continue
            for f in ('type', 'year', 'sem', 'rama'):
                if o[f] != e[f]:
                    if f == 'sem' and (c['id'], p, y) in covered:
                        continue
                    print('AUDIT DIFF %s %s %s field=%s data=%r raw=%r'
                          % (c['id'], p, y, f, o[f], e[f]))
                    bad += 1
    for key, o in c['occ'].items():
        p2 = key.rsplit('_', 1)[0]
        pv = (c['programs'].get(p2) or {})
        y2 = key.rsplit('_', 1)[1]
        if y2 in pv and o != pv[y2]:
            print('AUDIT occ/programs mismatch for', c['id'], key)
            bad += 1
print('audit: checked %d occurrences, %d divergence(s)%s'
      % (checked, bad, ' -- FAIL' if bad else ' -- OK'))
print('cross-listed courses (same program-year, multiple rama contexts):')
for (show, p, y), vals in sorted(multi.items()):
    if len(vals) > 1:
        print('  WARN %s %s %s contexts=%s' % (show, p, y, sorted(vals)))
if bad:
    sys.exit(1)

data = {"programs": list(programs.values()), "courses": list(courses.values()), "edges": edges,
        "extNames": ext, "meta": {"years": ["2025", "2026"],
        "counts": {"courses": len(courses), "edges": len(edges)}}}
json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('courses', len(courses), 'edges', len(edges),
      'pre', sum(1 for e in edges if e['kind'] == 'pre'),
      'co', sum(1 for e in edges if e['kind'] == 'co'), 'extNames', len(ext))
per = {}
for c in courses.values():
    for p, ys in c['programs'].items():
        for y in ys: per[(p, y)] = per.get((p, y), 0) + 1
print('per program-year:', sorted(per.items()))
