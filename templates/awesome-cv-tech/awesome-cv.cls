%----------------------------------------------------------------------------------------
%	CLASS IDENTIFICATION
%----------------------------------------------------------------------------------------
%
%% awesome-cv.cls
%% Copyright (C) 2015-2024 by Claud D. Park <posquit0.bj@gmail.com>
%% Modified work Copyright (C) 2024 by LaTeX Resume Generator Contributors
%%
%% Based on Awesome-CV: https://github.com/posquit0/Awesome-CV
%% 
%% This work may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either version 1.3c
%% of this license or (at your option) any later version.
%% The latest version of this license is in
%%   http://www.latex-project.org/lppl.txt
%% and version 1.3c or later is part of all distributions of LaTeX
%% version 2005/12/01 or later.
%%
%% This work has the LPPL maintenance status `maintained'.
%% 
%% The Current Maintainer of this work is the LaTeX Resume Generator Contributors.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{awesome-cv}[2025/01/01 v1.0 Awesome CV Class for Tech Professionals]

%----------------------------------------------------------------------------------------
%	CLASS OPTIONS
%----------------------------------------------------------------------------------------

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

%----------------------------------------------------------------------------------------
%	REQUIRED PACKAGES
%----------------------------------------------------------------------------------------

\RequirePackage[left=0.5in, right=0.5in, top=0.5in, bottom=0.5in]{geometry}
\RequirePackage{fontawesome5}
\RequirePackage{xcolor}
\RequirePackage{hyperref}
\RequirePackage{enumitem}
\RequirePackage{tabularx}
\RequirePackage[explicit]{titlesec}
\RequirePackage{parskip}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\RequirePackage{paracol}
\RequirePackage{multicol}
\RequirePackage{needspace}
\usetikzlibrary{calc}

%----------------------------------------------------------------------------------------
%	COLORS
%----------------------------------------------------------------------------------------

\definecolor{primary}{HTML}{2596be}      % Custom blue
\definecolor{secondary}{HTML}{1a7a9e}    % Darker blue
\definecolor{text}{RGB}{44, 62, 80}           % Dark text
\definecolor{accent}{RGB}{149, 165, 166}      % Light gray for accents
\definecolor{lightgray}{RGB}{245, 245, 245}   % Light background
\definecolor{sidebarbg}{RGB}{250, 250, 250}   % Sidebar background
\definecolor{black}{RGB}{0, 0, 0}             % Pure black

%----------------------------------------------------------------------------------------
%	HYPERLINKS
%----------------------------------------------------------------------------------------

\hypersetup{
    colorlinks=true,
    linkcolor=primary,
    urlcolor=primary,
    pdfborder={0 0 0}
}

%----------------------------------------------------------------------------------------
%	FONTS
%----------------------------------------------------------------------------------------

\RequirePackage[T1]{fontenc}
\RequirePackage[default]{lato}

%----------------------------------------------------------------------------------------
%	PAGE LAYOUT
%----------------------------------------------------------------------------------------

\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

%----------------------------------------------------------------------------------------
%	CUSTOM COMMANDS - HEADER
%----------------------------------------------------------------------------------------

\newcommand{\name}[1]{%
    \gdef\@name{#1}%
}

\newcommand{\position}[1]{%
    \gdef\@position{#1}%
}

\newcommand{\contact}[1]{%
    \gdef\@contact{#1}%
}

\newcommand{\photo}[1]{%
    \gdef\@photo{#1}%
}

\newcommand{\makeheader}{%
    \begin{center}
        {\fontsize{32}{36}\selectfont\bfseries\color{primary}\@name}\\[0.5em]
        {\fontsize{12}{14}\selectfont\color{secondary}\@position}\\[0.5em]
        {\fontsize{10}{12}\selectfont\color{text}\@contact}
    \end{center}
    \vspace{1em}
}

%----------------------------------------------------------------------------------------
%	CUSTOM COMMANDS - SECTIONS
%----------------------------------------------------------------------------------------

\titleformat{\section}
    {\needspace{4\baselineskip}\Large\bfseries\color{black}}
    {}
    {0em}
    {#1\hspace{0.5em}\color{primary}\leaders\hrule height 1.5pt\hfill\kern0pt}
    [\vspace{0.3em}]

\newcommand{\sidebarheading}[1]{%
    {\large\bfseries\color{black}#1\hspace{0.5em}\color{primary}\leaders\hrule height 1pt\hfill\kern0pt}\\[0.2em]
}

\newcommand{\colorheading}[2]{%
    {\color{primary}#1}{\color{black}#2}%
}

%----------------------------------------------------------------------------------------
%	CUSTOM COMMANDS - EXPERIENCE
%----------------------------------------------------------------------------------------

\newcommand{\experience}[5]{%
    \needspace{6\baselineskip}%
    \noindent
    {\textbf{\color{black}#1}\hfill\textbf{#2}}\\[0.1em]
    \noindent
    {\small\color{gray}\textit{#4}\hfill\textit{\color{accent}#3}}
    \vspace{0.3em}
    \begin{itemize}[leftmargin=2em, itemsep=0.2em, topsep=0.3em]
        #5
    \end{itemize}
    \vspace{0.4em}
}

%----------------------------------------------------------------------------------------
%	CUSTOM COMMANDS - SKILLS
%----------------------------------------------------------------------------------------

\newcommand{\skillcategory}[2]{%
    \textbf{\color{secondary}#1:} \color{text}#2\\[0.3em]
}

\newcommand{\sidebarskill}[1]{%
    {\linespread{0.7}\selectfont $\circ$ \color{text}#1\\[-0.005em]}
}

\newcommand{\sidebarskillcategory}[2]{%
    {\linespread{0.7}\selectfont\textbf{\color{black}#1}\\[0.002em]
    #2}
    \vspace{0.005em}
}

% Helper for skill category headings with first 3 letters in color
\newcommand{\skillcatheading}[2]{%
    \textbf{\color{primary}#1\color{black}#2}%
}

\newcommand{\contactitem}[2]{%
    {\color{primary}#1} \color{text}#2\\[0.1em]
}

%----------------------------------------------------------------------------------------
%	CUSTOM COMMANDS - CERTIFICATION
%----------------------------------------------------------------------------------------

\newcommand{\certification}[3]{%
    \begin{tabularx}{\textwidth}{@{}l X r@{}}
        \textbf{\color{black}#1} & \textit{#2} & \color{accent}#3
    \end{tabularx}
    \vspace{0.2em}
}

%----------------------------------------------------------------------------------------
%	CUSTOM COMMANDS - EDUCATION
%----------------------------------------------------------------------------------------

\newcommand{\education}[3]{%
    \begin{tabularx}{\textwidth}{@{}l X r@{}}
        \textbf{\color{black}#1} & \textit{#2} & \color{accent}#3
    \end{tabularx}
    \vspace{0.1em}
}

%----------------------------------------------------------------------------------------
%	END OF CLASS
%----------------------------------------------------------------------------------------
