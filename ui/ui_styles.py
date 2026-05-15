class UIStyleManager:
    def __init__(self):
        self.themes = {
            'light': {
                'bg': '#F7FAFC',
                'card_bg': '#FFFFFF',
                'primary': '#3182CE',
                'secondary': '#EDF2F7',
                'success': '#38A169',
                'warning': '#D69E2E',
                'danger': '#E53E3E',
                'text': '#2D3748',
                'text_secondary': '#4A5568',
                'border': '#E2E8F0',
                'hover': '#EDF2F7'
            },
            'dark': {
                'bg': '#1A202C',
                'card_bg': '#2D3748',
                'primary': '#63B3ED',
                'secondary': '#4A5568',
                'success': '#48BB78',
                'warning': '#F6E05E',
                'danger': '#FC8181',
                'text': '#F7FAFC',
                'text_secondary': '#A0AEC0',
                'border': '#4A5568',
                'hover': '#2D3748'
            }
        }

    def get_theme(self, theme_name='light'):
        return self.themes.get(theme_name, self.themes['light'])
