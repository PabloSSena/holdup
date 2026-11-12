"""English and Brazilian Portuguese copy, from the design. The English text is the key; tr() gives it in the User's
language: the one chosen in Settings, else the system display language (Portuguese, else English)."""
import ctypes
import sys
from datetime import date

LANGUAGE = "language"  # Store name of the language chosen in Settings ("en" or "pt"); absent follows the system
LANGUAGES = {"en": "English (US)", "pt": "Português (BR)"}  # each in its own language, as in the design


def system_language(platform: str = sys.platform) -> str:
    """Portuguese when the display language is (any region), else English. Not QLocale on Windows: it read English in
    the packaged app on a pt-BR Windows. On macOS and Linux QLocale reads the User's preferred languages."""
    if platform == "win32":
        return "pt" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x16 else "en"  # LANG_PORTUGUESE
    from PySide6.QtCore import QLocale

    languages = QLocale.system().uiLanguages()
    return "pt" if languages and languages[0].lower().startswith("pt") else "en"


def start_at_login_copy(platform: str = sys.platform) -> tuple[str, str]:
    """The Start at login setting's title and note, in English (the tr() key). Windows users know it by its name."""
    if platform == "win32":
        return "Start with Windows", "Holdup starts in the tray when you sign in."
    return "Start at login", "Holdup starts in the tray when you log in."


LANG = system_language()  # tray.py replaces it with the Settings choice before building any window

_PT = {
    # shell and status
    "Today": "Hoje", "History": "Histórico", "Settings": "Configurações", "Yesterday": "Ontem",
    "Watching": "Monitorando", "Absent": "Ausente", "Camera Unavailable": "Câmera Indisponível",
    "Stale Baseline": "Referência Desatualizada", "Paused": "Pausado", "Calibrating": "Calibrando",
    "Uncalibrated": "Não calibrado",
    "Good Posture": "Boa Postura", "Forward Lean": "Inclinação para Frente", "Side Lean": "Inclinação Lateral",
    "Mirror": "Espelho", "Watched Time": "Tempo Monitorado", "Bad Posture": "Má Postura", "Baseline": "Referência",
    # Today
    "You are sitting well. Holdup is quietly keeping an eye on your posture.":
        "Você está com uma boa postura. O Holdup está de olho, discretamente.",
    "Nobody is in front of the camera. Watching picks up again when you are back.":
        "Ninguém está em frente à câmera. O monitoramento volta quando você retornar.",
    "Watching is on hold until the camera can be read.": "O monitoramento está em espera até a câmera poder ser lida.",
    "Watching is on hold until you Recalibrate.": "O monitoramento está em espera até você Recalibrar.",
    "Holdup is not watching right now. Your Watched Time is not counting.":
        "O Holdup não está monitorando agora. O Tempo Monitorado não está contando.",
    "Capturing your Baseline. Hold still for a moment.": "Capturando sua Referência. Fique parado por um instante.",
    "Paused until {}": "Pausado até {}", "Paused until resumed": "Pausado até retomar", "since {}": "desde {}",
    "Pause for 30 minutes": "Pausar por 30 minutos", "Pause for 1 hour": "Pausar por 1 hora",
    "Pause until resumed": "Pausar até retomar", "Resume": "Retomar", "Recalibrate": "Recalibrar",
    "Holdup can't read your camera": "O Holdup não consegue ler sua câmera",
    "It may be unplugged, covered, or in use by another app such as a video call. Holdup keeps trying on its own and "
    "starts watching again when the camera is free.":
        "Ela pode estar desconectada, coberta ou em uso por outro app, como uma chamada de vídeo. O Holdup continua "
        "tentando sozinho e volta a monitorar quando a câmera estiver livre.",
    "Try again": "Tentar novamente", "Choose another camera": "Escolher outra câmera",
    "Your camera view has changed": "A imagem da câmera mudou",
    "Your Baseline no longer matches what the camera sees, so Holdup has stopped watching for now. Recalibrate and it "
    "picks up right away.":
        "Sua Referência não corresponde mais ao que a câmera vê, por isso o Holdup parou de monitorar por enquanto. "
        "Recalibre e ele volta na hora.",
    "times today": "vezes hoje",
    "The Mirror shows you your camera picture when Bad Posture lasts too long.":
        "O Espelho mostra a imagem da sua câmera quando a Má Postura dura tempo demais.",
    # History
    "Last {} days": "Últimos {} dias", "Clear statistics": "Limpar estatísticas",
    "No Daily Stats yet": "Ainda não há Estatísticas Diárias",
    "Once Holdup has watched you for a while, each day's Good Posture, Forward Lean and Side Lean show up here.":
        "Depois que o Holdup monitorar você por um tempo, a Boa Postura, a Inclinação para Frente e a Inclinação "
        "Lateral de cada dia aparecem aqui.",
    "Good Posture per day": "Boa Postura por dia", "Average": "Média de",
    "across {} days with Watched Time": "em {} dias com Tempo Monitorado",
    "across {} day with Watched Time": "em {} dia com Tempo Monitorado",
    "No Watched Time in these days": "Sem Tempo Monitorado nestes dias",
    "Daily Stats": "Estatísticas Diárias", "Day": "Dia", "No Watched Time": "Sem Tempo Monitorado",
    "Good Posture {}%": "Boa Postura {}%",
    "Delete all Daily Stats?": "Excluir todas as Estatísticas Diárias?",
    "Your Baseline and settings are kept.": "Sua Referência e suas configurações serão mantidas.",
    "Cancel": "Cancelar", "Delete Daily Stats": "Excluir Estatísticas Diárias",
    # Settings
    "Sensitivity": "Sensibilidade",
    "How far from your Baseline you may sit before it counts as Bad Posture.":
        "Quanto você pode se afastar da sua Referência antes de contar como Má Postura.",
    "Low": "Baixa", "Medium": "Média", "High": "Alta",
    "You can move quite a bit away from your Baseline before it counts as Bad Posture.":
        "Você pode se afastar bastante da sua Referência antes de contar como Má Postura.",
    "A balanced margin around your Baseline. Good for most people.":
        "Uma margem equilibrada em torno da sua Referência. Boa para a maioria das pessoas.",
    "Only small shifts away from your Baseline are allowed. Good if you want a firm nudge.":
        "Só pequenos desvios da sua Referência são permitidos. Boa se você quer um lembrete firme.",
    "Camera": "Câmera", "Choose a camera": "Escolha uma câmera", "No camera found": "Nenhuma câmera encontrada",
    "Plug in a camera and it shows up here.": "Conecte uma câmera e ela aparecerá aqui.",
    "Switching camera makes your Baseline Stale. You'll be asked to Recalibrate before watching resumes.":
        "Trocar de câmera deixa sua Referência Desatualizada. Será preciso Recalibrar antes de o monitoramento voltar.",
    "Needs a camera": "Precisa de uma câmera",
    "Stale — the camera view changed. Recalibrate to resume watching.":
        "Desatualizada — a imagem da câmera mudou. Recalibre para voltar a monitorar.",
    "Not captured yet": "Ainda não capturada", "Captured": "Capturada",
    "Captured today at {}": "Capturada hoje às {}", "Captured {} at {}": "Capturada em {} às {}",
    "Start with Windows": "Iniciar com o Windows",
    "Holdup starts in the tray when you sign in.": "O Holdup abre na bandeja quando você entra no Windows.",
    "Start at login": "Iniciar ao entrar",
    "Holdup starts in the tray when you log in.": "O Holdup abre na bandeja quando você entra no computador.",
    "Your camera picture stays with you": "A imagem da sua câmera fica com você",
    "Frames never leave this computer and are never saved. Holdup keeps only numbers, like how many minutes you sat "
    "in Good Posture.":
        "As imagens nunca saem deste computador e nunca são salvas. O Holdup guarda apenas números, como quantos "
        "minutos você ficou em Boa Postura.",
    # Calibration
    "Calibration": "Calibração", "Live preview": "Prévia ao vivo", "No picture": "Sem imagem",
    "Start": "Iniciar", "Retry": "Tentar novamente", "Done": "Concluir",
    "Get ready": "Prepare-se", "Capturing": "Capturando", "All set": "Tudo pronto",
    "Let’s try again": "Vamos tentar de novo",
    "Sit up straight, the way you want to sit, facing your screen.":
        "Sente-se com a postura ereta, do jeito que você quer ficar, de frente para a tela.",
    "Holdup captures this as your Baseline. It takes about five seconds.":
        "O Holdup captura isso como sua Referência. Leva cerca de cinco segundos.",
    "Capturing in {}…": "Capturando em {}…", "Hold still…": "Fique parado…",
    "Keep looking at your screen for a moment.": "Continue olhando para a tela por um instante.",
    "Your Baseline is captured.": "Sua Referência foi capturada.",
    "Holdup is now watching your posture.": "O Holdup agora está monitorando sua postura.",
    "Make sure you are in view and hold still": "Verifique se você está visível e fique parado",
    "Your head and shoulders should sit inside the outline.": "Sua cabeça e seus ombros devem ficar dentro do contorno.",
    "The camera can't be read": "Não é possível ler a câmera",
    "Check that it is plugged in, not covered, and not being used by another app.":
        "Verifique se ela está conectada, descoberta e sem uso por outro app.",
    "Language": "Idioma",
    "Holdup restarts to switch language.": "O Holdup reinicia para trocar o idioma.",
    # tray (not in the design; same words)
    "Open Holdup": "Abrir o Holdup", "Quit": "Sair",
    "Holdup: camera view changed": "Holdup: a imagem da câmera mudou",
    "Your Baseline no longer fits. Choose Recalibrate in the tray menu to resume watching.":
        "Sua Referência não serve mais. Escolha Recalibrar no menu da bandeja para voltar a monitorar.",
    # dates
    "{weekday} {day} {month}": "{weekday}, {day} {month}",
    "{weekday}, {day} {month}": "{weekday}, {day} de {month}",
}

_WEEKDAYS = {"en": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
             "pt": ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")}
_WEEKDAYS_FULL = {"en": ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
                  "pt": ("Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado",
                         "Domingo")}
_MONTHS = {"en": ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
           "pt": ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")}
_MONTHS_FULL = {"en": ("January", "February", "March", "April", "May", "June", "July", "August", "September",
                       "October", "November", "December"),
                "pt": ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
                       "outubro", "novembro", "dezembro")}


def tr(text: str) -> str:
    return _PT.get(text, text) if LANG == "pt" else text


def weekday(day: date) -> str:
    """Not strftime: that follows the C locale, not the User's language."""
    return _WEEKDAYS[LANG][day.weekday()]


def day_month(day: date) -> str:
    """ "14 Oct" / "14 out"."""
    return f"{day.day} {_MONTHS[LANG][day.month - 1]}"


def short_date(day: date) -> str:
    """ "Wed 14 Oct" / "Qua, 14 out"."""
    return tr("{weekday} {day} {month}").format(weekday=weekday(day), day=day.day, month=_MONTHS[LANG][day.month - 1])


def long_date(day: date) -> str:
    """ "Friday, 16 October" / "Sexta-feira, 16 de outubro"."""
    return tr("{weekday}, {day} {month}").format(weekday=_WEEKDAYS_FULL[LANG][day.weekday()], day=day.day,
                                                 month=_MONTHS_FULL[LANG][day.month - 1])
