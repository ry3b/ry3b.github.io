r"""CV/resume visual styles. A style is a preamble that defines the layout
macros the renderer emits: \cvhead, \cventry, \cvpaper, \courseline, cvbullets.
"""

COMMON = r"""
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{etoolbox}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\pagestyle{empty}
\setlength{\parindent}{0pt}
% loud marker for data that is not in cv.json yet
\newcommand{\FILL}[1]{{\bfseries\color{red}[#1?]}}
\newcommand{\contactsep}{\,\textperiodcentered\,}
\newcommand{\ifne}[2]{\notblank{#1}{#2}{}}
"""




TIMES = COMMON + r"""
\usepackage[margin=1in]{geometry}
\usepackage{newtxtext}
\titleformat{\section}{\normalfont\bfseries\large}{}{0em}{}[\vspace{-8pt}\rule{\textwidth}{0.4pt}]
\titlespacing*{\section}{0pt}{15pt}{7pt}
\newcommand{\cvhead}[2]{%
  \begin{center}
    {\LARGE #1}\\[5pt]
    {\small #2}
  \end{center}\vspace{2pt}}
\newcommand{\tworow}[2]{%
  \noindent\begin{minipage}[t]{0.735\textwidth}\raggedright #1\end{minipage}\hfill
  \begin{minipage}[t]{0.245\textwidth}\raggedleft #2\end{minipage}\par}
\newcommand{\cventry}[4]{%
  \par\vspace{5pt}%
  \tworow{\textbf{#2}}{\small #1}%
  \ifne{#3#4}{\tworow{\small\itshape #3}{\small #4}}}
\newcommand{\cvpaper}[4]{%
  \par\vspace{5pt}%
  \textbf{#1}\par
  \ifne{#2}{{\small #2}\par}%
  \ifne{#3}{{\small\itshape #3}\par}%
  \ifne{#4}{{\small #4}\par}}
\newcommand{\courseline}[2]{\par\vspace{4pt}\textbf{#1.} #2\par}
\newlist{cvbullets}{itemize}{1}
\setlist[cvbullets]{leftmargin=1.3em,topsep=3pt,itemsep=1pt,parsep=0pt,label=\textendash}
"""

# Resume: every line is linear text in reading order, so a parser reads it the
# way a person does. No minipages, no tabulars, no right-aligned columns --
# pdftotext detaches all of those from their entry.
ATS = COMMON + r"""
\usepackage[margin=0.8in]{geometry}
\usepackage{newtxtext}
\titleformat{\section}{\normalfont\bfseries\normalsize}{}{0em}{\MakeUppercase}[\vspace{-8pt}\rule{\textwidth}{0.4pt}]
\titlespacing*{\section}{0pt}{13pt}{6pt}
\renewcommand{\contactsep}{\ \textbar\ }
\newcommand{\cvhead}[2]{%
  \begin{center}
    {\LARGE\bfseries #1}\\[4pt]
    {\small #2}
  \end{center}\vspace{1pt}}
\newcommand{\cventry}[4]{%
  \par\vspace{5pt}%
  \textbf{#2}\par
  \ifne{#3#4#1}{{\small #3\ifne{#4}{, #4}\ifne{#1}{ \textbar{} #1}}\par}}
\newcommand{\cvpaper}[4]{%
  \par\vspace{5pt}%
  \textbf{#1}\par\ifne{#2}{{\small #2}\par}\ifne{#3}{{\small #3}\par}\ifne{#4}{{\small #4}\par}}
\newcommand{\courseline}[2]{\par\vspace{3pt}{\small\textbf{#1}: #2}\par}
\newlist{cvbullets}{itemize}{1}
\setlist[cvbullets]{leftmargin=1.2em,topsep=2pt,itemsep=1pt,parsep=0pt,label=\textbullet}
"""

DOCCLASS = r"\documentclass[11pt]{article}"

STYLES = {
    "times": {"preamble": DOCCLASS + TIMES},
    "ats": {"preamble": DOCCLASS + ATS},
}
