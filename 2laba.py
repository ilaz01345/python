"""
ПРОГРАММА ДЛЯ ПОИСКА ГИПЕРССЫЛОК В HTML
Лабораторная работа №2
"""

import re
from typing import List, Dict


class HTMLLinkFinder:
    """Класс для поиска гиперссылок в HTML"""
    
    def __init__(self):
        # Основные регулярные выражения для поиска ссылок
        self.patterns = {
            'ссылки_a': r'<a\s+[^>]*?href="([^"]*)"',
            'ссылки_img': r'<img\s+[^>]*?src="([^"]*)"',
            'ссылки_link': r'<link\s+[^>]*?href="([^"]*)"',
            'ссылки_script': r'<script\s+[^>]*?src="([^"]*)"',
            'ссылки_form': r'<form\s+[^>]*?action="([^"]*)"',
        }
    
    def find_all_links(self, html: str) -> Dict[str, List[str]]:
        """
        Найти все ссылки в HTML-коде
        
        Args:
            html: HTML-код для анализа
            
        Returns:
            Словарь с типами ссылок и их значениями
        """
        results = {}
        
        for link_type, pattern in self.patterns.items():
            try:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    # Фильтруем и очищаем найденные ссылки
                    cleaned_matches = []
                    for match in matches:
                        if match and match.strip():
                            cleaned_matches.append(match.strip())
                    
                    if cleaned_matches:
                        results[link_type] = cleaned_matches
            except Exception:
                continue
        
        return results
    
    def analyze_results(self, links_dict: Dict[str, List[str]]) -> Dict:
        """
        Проанализировать найденные ссылки
        
        Args:
            links_dict: Словарь с найденными ссылками
            
        Returns:
            Словарь с результатами анализа
        """
        # Собираем все ссылки в один список
        all_links = []
        for link_list in links_dict.values():
            all_links.extend(link_list)
        
        # Анализируем типы ссылок
        http_links = []
        https_links = []
        relative_links = []
        special_links = []
        other_links = []
        
        for link in all_links:
            link_lower = link.lower()
            
            if link_lower.startswith('http://'):
                http_links.append(link)
            elif link_lower.startswith('https://'):
                https_links.append(link)
            elif link_lower.startswith(('/', './', '../')):
                relative_links.append(link)
            elif link_lower.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                special_links.append(link)
            else:
                other_links.append(link)
        
        return {
            'всего_ссылок': len(all_links),
            'уникальных': len(set(all_links)),
            'дубликатов': len(all_links) - len(set(all_links)),
            'по_типам': {
                'http': len(http_links),
                'https': len(https_links),
                'относительные': len(relative_links),
                'специальные': len(special_links),
                'прочие': len(other_links),
            }
        }


def show_example_html() -> str:
    """Вернуть пример HTML-кода с ссылками"""
    example = '''<!DOCTYPE html>
<html>
<head>
    <title>Пример веб-страницы</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>Мой сайт</h1>
        <nav>
            <a href="https://google.com">Google</a>
            <a href="/about.html">О нас</a>
            <a href="#contacts">Контакты</a>
        </nav>
    </header>
    
    <main>
        <section>
            <h2>Галерея</h2>
            <img src="images/photo1.jpg" alt="Фото 1">
            <img src="https://example.com/photo2.jpg" alt="Фото 2">
        </section>
        
        <section>
            <h2>Поиск</h2>
            <form action="/search" method="GET">
                <input type="text" name="query">
                <button type="submit">Найти</button>
            </form>
        </section>
    </main>
    
    <footer>
        <script src="js/main.js"></script>
    </footer>
</body>
</html>'''
    
    return example


def display_analysis_results(links_dict: Dict[str, List[str]], analysis: Dict):
    """Отобразить результаты анализа"""
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ПОИСКА ССЫЛОК В HTML")
    print("=" * 70)
    
    print(f"\n📊 Статистика:")
    print(f"   Всего ссылок: {analysis['всего_ссылок']}")
    print(f"   Уникальных: {analysis['уникальных']}")
    print(f"   Дубликатов: {analysis['дубликатов']}")
    
    print(f"\n📈 Распределение по типам:")
    for link_type, count in analysis['по_типам'].items():
        print(f"   {link_type}: {count}")
    
    print(f"\n🔗 Найденные ссылки:")
    print("-" * 50)
    
    total_shown = 0
    for link_type, links in links_dict.items():
        if links:
            # Преобразуем название типа в читаемый формат
            readable_type = link_type.replace('ссылки_', '').upper()
            print(f"\n{readable_type} ({len(links)}):")
            
            for i, link in enumerate(links, 1):
                print(f"  {i}. {link}")
                total_shown += 1
    
    print(f"\n👁️  Всего показано: {total_shown} ссылок")
    print("=" * 70)


def main():
    """Главная функция программы"""
    finder = HTMLLinkFinder()
    
    print("=" * 70)
    print("ПОИСК ГИПЕРССЫЛОК В HTML-ДОКУМЕНТАХ")
    print("=" * 70)
    print("Программа находит и анализирует все ссылки в HTML-коде")
    print("Использует регулярные выражения для точного поиска")
    print("=" * 70)
    
    while True:
        print("\n" + "-" * 40)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 40)
        print("1. 🔍 Ввести HTML код и найти ссылки")
        print("2. 📋 Использовать пример HTML")
        print("3. ℹ️  Показать информацию о программе")
        print("4. 🚪 Выход")
        print("-" * 40)
        
        try:
            choice = input("\nВыберите пункт (1-4): ").strip()
            
            if choice == '1':
                print("\n" + "-" * 40)
                print("ВВОД HTML КОДА")
                print("-" * 40)
                print("Введите HTML код (для завершения введите 'END' на новой строке):")
                print("-" * 40)
                
                lines = []
                while True:
                    line = input()
                    if line.upper() == 'END':
                        break
                    lines.append(line)
                
                if lines:
                    html_content = '\n'.join(lines)
                    print("\n⏳ Анализирую HTML код...")
                    
                    # Ищем ссылки
                    links_dict = finder.find_all_links(html_content)
                    
                    # Анализируем результаты
                    analysis = finder.analyze_results(links_dict)
                    
                    # Показываем результаты
                    display_analysis_results(links_dict, analysis)
                else:
                    print("\n❌ HTML код не был введен")
            
            elif choice == '2':
                print("\n" + "-" * 40)
                print("ПРИМЕР HTML КОДА")
                print("-" * 40)
                
                example = show_example_html()
                print("Пример HTML кода с различными типами ссылок:")
                print("-" * 40)
                print(example)
                print("-" * 40)
                
                use_example = input("\nПроанализировать этот пример? (да/нет): ").strip().lower()
                if use_example in ['да', 'д', 'y', 'yes']:
                    print("\n⏳ Анализирую пример HTML...")
                    
                    # Ищем ссылки в примере
                    links_dict = finder.find_all_links(example)
                    
                    # Анализируем результаты
                    analysis = finder.analyze_results(links_dict)
                    
                    # Показываем результаты
                    display_analysis_results(links_dict, analysis)
            
            elif choice == '3':
                print("\n" + "=" * 70)
                print("ИНФОРМАЦИЯ О ПРОГРАММЕ")
                print("=" * 70)
                print("\n📋 Программа для лабораторной работы №2")
                print("\n🔍 Что делает программа:")
                print("   • Ищет все гиперссылки в HTML-документах")
                print("   • Использует регулярные выражения для поиска")
                print("   • Анализирует типы найденных ссылок")
                print("   • Показывает статистику по ссылкам")
                
                print("\n📝 Регулярные выражения, которые использует программа:")
                for pattern_name, pattern in finder.patterns.items():
                    readable_name = pattern_name.replace('ссылки_', 'Для ')
                    print(f"   • {readable_name}: {pattern}")
                
                print("\n💡 Пример использования:")
                print("   html = '<a href=\"https://example.com\">Ссылка</a>'")
                print("   links = finder.find_all_links(html)")
                print("   print(links)  # Выведет найденные ссылки")
                print("=" * 70)
            
            elif choice == '4':
                print("\n" + "=" * 50)
                print("Спасибо за использование программы!")
                print("До свидания!")
                print("=" * 50)
                break
            
            else:
                print("\n❌ Неверный выбор. Пожалуйста, введите число от 1 до 4.")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Программа прервана пользователем")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")
            print("Попробуйте еще раз")


# Запуск программы
if __name__ == "__main__":
    main()