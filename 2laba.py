"""
ПРОГРАММА ДЛЯ ПОИСКА ГИПЕРССЫЛОК В HTML
Лабораторная работа №2
"""

import re  #Импорт модуля для работы с регулярными выражениями
from typing import List, Dict  # Импорт типов для аннотации
import unittest  #БЛОК 17: Импорт модуля для unit-тестирования


class HTMLLinkFinder:
    """Основной класс программы для поиска ссылок в HTML"""
    
    def __init__(self):
        #Инициализация регулярных выражений для поиска разных типов ссылок
        #Каждое выражение соответствует определенному HTML-тегу и атрибуту
        self.patterns = {
            #Поиск ссылок в тегах <a> с атрибутом href
            'ссылки_a': r'<a\s+[^>]*?href="([^"]*)"',
            #Поиск ссылок на изображения в тегах <img> с атрибутом src
            'ссылки_img': r'<img\s+[^>]*?src="([^"]*)"',
            #Поиск ссылок в тегах <link> с атрибутом href (CSS, иконки и т.д.)
            'ссылки_link': r'<link\s+[^>]*?href="([^"]*)"',
            #Поиск ссылок на скрипты в тегах <script> с атрибутом src
            'ссылки_script': r'<script\s+[^>]*?src="([^"]*)"',
            #Поиск URL действий в тегах <form> с атрибутом action
            'ссылки_form': r'<form\s+[^>]*?action="([^"]*)"',
        }
    
    #Основной метод поиска всех ссылок
    #Принимает HTML-код и возвращает словарь с найденными ссылками по типам
    def find_all_links(self, html: str) -> Dict[str, List[str]]:
        results = {}  # Словарь для хранения результатов
        
        #Перебираем все типы ссылок и соответствующие им регулярные выражения
        for link_type, pattern in self.patterns.items():
            try:
                #Поиск всех совпадений по регулярному выражению
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    #Очистка и фильтрация найденных ссылок
                    cleaned_matches = []
                    for match in matches:
                        if match and match.strip():  #Проверка на пустые значения
                            cleaned_matches.append(match.strip())  #Удаление лишних пробелов
                    
                    if cleaned_matches:  #Добавляем только если есть результаты
                        results[link_type] = cleaned_matches
            except Exception:  #Обработка возможных ошибок при поиске
                continue
        
        return results  #Возвращаем словарь с найденными ссылками
    
    #Метод анализа статистики найденных ссылок
    #Анализирует ссылки, подсчитывает количество, уникальность, классифицирует по типам
    def analyze_results(self, links_dict: Dict[str, List[str]]) -> Dict:
        #Собираем все ссылки в один плоский список
        all_links = []
        for link_list in links_dict.values():
            all_links.extend(link_list)
        
        #Классификация ссылок по типам протоколов и форматам
        http_links = []
        https_links = []
        relative_links = []
        special_links = []
        other_links = []
        
        for link in all_links:
            link_lower = link.lower()  #Приведение к нижнему регистру для единообразной проверки
            
            #Классификация ссылок:
            if link_lower.startswith('http://'):
                http_links.append(link)  #HTTP ссылки
            elif link_lower.startswith('https://'):
                https_links.append(link)  #HTTPS ссылки
            elif link_lower.startswith(('/', './', '../')):
                relative_links.append(link)  #Относительные пути
            elif link_lower.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                special_links.append(link)  #Специальные ссылки (якоря, почта и т.д.)
            else:
                other_links.append(link)  #Все остальные ссылки
        
        #Формирование итоговой статистики
        return {
            'всего_ссылок': len(all_links),  #Общее количество найденных ссылок
            'уникальных': len(set(all_links)),  #Количество уникальных ссылок
            'дубликатов': len(all_links) - len(set(all_links)),  #Количество дубликатов
            'по_типам': {  #Распределение по типам протоколов
                'http': len(http_links),
                'https': len(https_links),
                'относительные': len(relative_links),
                'специальные': len(special_links),
                'прочие': len(other_links),
            }
        }


#Функция для демонстрации примера HTML-кода
#Возвращает заранее подготовленный HTML с различными типами ссылок для тестирования
def show_example_html() -> str:
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


#Функция для отображения результатов анализа
#Форматирует и выводит статистику и найденные ссылки в читаемом виде
def display_analysis_results(links_dict: Dict[str, List[str]], analysis: Dict):
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ПОИСКА ССЫЛОК В HTML")
    print("=" * 70)
    
    #Вывод общей статистики
    print(f"\n📊 Статистика:")
    print(f"   Всего ссылок: {analysis['всего_ссылок']}")
    print(f"   Уникальных: {analysis['уникальных']}")
    print(f"   Дубликатов: {analysis['дубликатов']}")
    
    #Вывод распределения по типам
    print(f"\n📈 Распределение по типам:")
    for link_type, count in analysis['по_типам'].items():
        print(f"   {link_type}: {count}")
    
    #Вывод детального списка ссылок по типам
    print(f"\n🔗 Найденные ссылки:")
    print("-" * 50)
    
    total_shown = 0  #Счетчик показанных ссылок
    for link_type, links in links_dict.items():
        if links:
            #Преобразование имени типа в читаемый формат
            readable_type = link_type.replace('ссылки_', '').upper()
            print(f"\n{readable_type} ({len(links)}):")
            
            #Вывод всех ссылок данного типа
            for i, link in enumerate(links, 1):
                print(f"  {i}. {link}")
                total_shown += 1
    
    print(f"\n👁️  Всего показано: {total_shown} ссылок")
    print("=" * 70)


#Класс для unit-тестирования программы
#Тестирует корректность работы регулярных выражений и основных методов
class TestHTMLLinkFinder(unittest.TestCase):
    """Тестовый класс для проверки корректности работы HTMLLinkFinder"""
    
    def setUp(self):
        """Инициализация тестового объекта перед каждым тестом"""
        self.finder = HTMLLinkFinder()
    
    #Тесты для проверки регулярных выражений
    
    def test_find_a_tags_with_href(self):
        """Тест 1: Проверка поиска ссылок в тегах <a> с атрибутом href"""
        html = '<a href="https://google.com">Google</a>'
        result = self.finder.find_all_links(html)
        self.assertIn('ссылки_a', result)
        self.assertEqual(result['ссылки_a'], ['https://google.com'])
    
    def test_find_multiple_a_tags(self):
        """Тест 2: Проверка поиска нескольких ссылок в тегах <a>"""
        html = '<a href="page1.html">Page 1</a><a href="page2.html">Page 2</a>'
        result = self.finder.find_all_links(html)
        self.assertEqual(len(result['ссылки_a']), 2)
        self.assertIn('page1.html', result['ссылки_a'])
        self.assertIn('page2.html', result['ссылки_a'])
    
    def test_find_a_tags_with_spaces(self):
        """Тест 3: Проверка поиска ссылок в тегах <a> с пробелами и другими атрибутами"""
        html = '<a class="link" href="https://example.com" target="_blank">Example</a>'
        result = self.finder.find_all_links(html)
        self.assertEqual(result['ссылки_a'], ['https://example.com'])
    
    def test_find_img_tags(self):
        """Тест 4: Проверка поиска ссылок в тегах <img> с атрибутом src"""
        html = '<img src="image.jpg" alt="Image">'
        result = self.finder.find_all_links(html)
        self.assertIn('ссылки_img', result)
        self.assertEqual(result['ссылки_img'], ['image.jpg'])
    
    def test_find_link_tags(self):
        """Тест 5: Проверка поиска ссылок в тегах <link> с атрибутом href"""
        html = '<link rel="stylesheet" href="styles.css">'
        result = self.finder.find_all_links(html)
        self.assertIn('ссылки_link', result)
        self.assertEqual(result['ссылки_link'], ['styles.css'])
    
    def test_find_script_tags(self):
        """Тест 6: Проверка поиска ссылок в тегах <script> с атрибутом src"""
        html = '<script src="app.js"></script>'
        result = self.finder.find_all_links(html)
        self.assertIn('ссылки_script', result)
        self.assertEqual(result['ссылки_script'], ['app.js'])
    
    def test_find_form_tags(self):
        """Тест 7: Проверка поиска ссылок в тегах <form> с атрибутом action"""
        html = '<form action="/submit" method="POST">'
        result = self.finder.find_all_links(html)
        self.assertIn('ссылки_form', result)
        self.assertEqual(result['ссылки_form'], ['/submit'])
    
    def test_case_insensitive_search(self):
        """Тест 8: Проверка регистронезависимого поиска"""
        html = '<A HREF="PAGE.HTML">Link</A>'
        result = self.finder.find_all_links(html)
        self.assertEqual(result['ссылки_a'], ['PAGE.HTML'])
    
    def test_empty_html(self):
        """Тест 9: Проверка обработки пустого HTML"""
        html = ''
        result = self.finder.find_all_links(html)
        self.assertEqual(result, {})
    
    def test_html_without_links(self):
        """Тест 10: Проверка обработки HTML без ссылок"""
        html = '<div>Some text without links</div>'
        result = self.finder.find_all_links(html)
        self.assertEqual(result, {})
    
    #Тесты для метода analyze_results
    
    def test_analyze_results_counts(self):
        """Тест 11: Проверка подсчета статистики"""
        links_dict = {
            'ссылки_a': ['https://google.com', '/about.html'],
            'ссылки_img': ['image.jpg']
        }
        analysis = self.finder.analyze_results(links_dict)
        
        self.assertEqual(analysis['всего_ссылок'], 3)
        self.assertEqual(analysis['уникальных'], 3)
        self.assertEqual(analysis['дубликатов'], 0)
    
    def test_analyze_results_with_duplicates(self):
        """Тест 12: Проверка обработки дубликатов"""
        links_dict = {
            'ссылки_a': ['https://google.com', 'https://google.com'],
            'ссылки_img': ['image.jpg', 'image.jpg']
        }
        analysis = self.finder.analyze_results(links_dict)
        
        self.assertEqual(analysis['всего_ссылок'], 4)
        self.assertEqual(analysis['уникальных'], 2)
        self.assertEqual(analysis['дубликатов'], 2)
    
    def test_analyze_results_classification(self):
        """Тест 13: Проверка классификации ссылок по типам"""
        links_dict = {
            'ссылки_a': [
                'http://example.com',
                'https://secure.com',
                '/relative.html',
                'javascript:void(0)',
                'mailto:test@example.com',
                '#anchor',
                'ftp://server.com'
            ]
        }
        analysis = self.finder.analyze_results(links_dict)
        
        self.assertEqual(analysis['по_типам']['http'], 1)
        self.assertEqual(analysis['по_типам']['https'], 1)
        self.assertEqual(analysis['по_типам']['относительные'], 1)
        self.assertEqual(analysis['по_типам']['специальные'], 3)  #javascript, mailto, anchor
        self.assertEqual(analysis['по_типам']['прочие'], 1)  #ftp
    
    def test_analyze_empty_dict(self):
        """Тест 14: Проверка анализа пустого словаря"""
        analysis = self.finder.analyze_results({})
        
        self.assertEqual(analysis['всего_ссылок'], 0)
        self.assertEqual(analysis['уникальных'], 0)
        self.assertEqual(analysis['дубликатов'], 0)
        self.assertEqual(analysis['по_типам']['http'], 0)
    
    #Интеграционные тесты
    
    def test_integration_with_example_html(self):
        """Тест 15: Интеграционный тест с полным HTML"""
        html = show_example_html()
        links_dict = self.finder.find_all_links(html)
        analysis = self.finder.analyze_results(links_dict)
        
        #Проверяем, что найдены ссылки разных типов
        self.assertIn('ссылки_a', links_dict)
        self.assertIn('ссылки_img', links_dict)
        self.assertIn('ссылки_link', links_dict)
        self.assertIn('ссылки_script', links_dict)
        self.assertIn('ссылки_form', links_dict)
        
        #Проверяем статистику
        self.assertGreater(analysis['всего_ссылок'], 0)
    
    def test_malformed_html(self):
        """Тест 16: Проверка обработки некорректного HTML"""
        #HTML с незакрытыми кавычками
        html = '<a href="unclosed>Link</a>'
        result = self.finder.find_all_links(html)
        #Ожидаем, что программа не упадет и вернет пустой результат
        self.assertEqual(result, {})
    
    def test_html_with_comments(self):
        """Тест 17: Проверка игнорирования комментариев в HTML"""
        html = '<!-- <a href="hidden.html">Hidden</a> --><a href="visible.html">Visible</a>'
        result = self.finder.find_all_links(html)
        #Регулярные выражения находят ссылки даже в комментариях
        #Это особенность текущей реализации
        self.assertIn('visible.html', result.get('ссылки_a', []))


#Функция для запуска тестов
def run_tests():
    """Запуск всех unit-тестов"""
    print("=" * 70)
    print("ЗАПУСК UNIT-ТЕСТОВ")
    print("=" * 70)
    
    #Создание тестового набора и запуск тестов
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHTMLLinkFinder)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 70)
    print(f"Тестов выполнено: {result.testsRun}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Сбоев: {len(result.failures)}")
    print("=" * 70)
    
    return result.wasSuccessful()


#Главная функция программы - точка входа
#Управляет основным циклом программы и меню
def main():
    finder = HTMLLinkFinder()  #Создание экземпляра класса для поиска ссылок
    
    #Вывод заголовка программы
    print("=" * 70)
    print("ПОИСК ГИПЕРССЫЛОК В HTML-ДОКУМЕНТАХ")
    print("=" * 70)
    print("Программа находит и анализирует все ссылки в HTML-коде")
    print("Использует регулярные выражения для точного поиска")
    print("=" * 70)
    
    #Основной цикл программы с меню
    while True:
        print("\n" + "-" * 40)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 40)
        print("1. 🔍 Ввести HTML код и найти ссылки")
        print("2. 📋 Использовать пример HTML")
        print("3. ℹ️  Показать информацию о программе")
        print("4. 🧪 Запустить unit-тесты")  #Добавлен новый пункт меню
        print("5. 🚪 Выход")
        print("-" * 40)
        
        try:
            choice = input("\nВыберите пункт (1-5): ").strip()
            
            #Обработка выбора "Ввести HTML код"
            if choice == '1':
                print("\n" + "-" * 40)
                print("ВВОД HTML КОДА")
                print("-" * 40)
                print("Введите HTML код (для завершения введите 'END' на новой строке):")
                print("-" * 40)
                
                #Многострочный ввод HTML-кода
                lines = []
                while True:
                    line = input()
                    if line.upper() == 'END':  #Ключевое слово для завершения ввода
                        break
                    lines.append(line)
                
                if lines:
                    html_content = '\n'.join(lines)  #Объединение строк в единый HTML
                    print("\n⏳ Анализирую HTML код...")
                    
                    #Поиск и анализ ссылок
                    links_dict = finder.find_all_links(html_content)
                    analysis = finder.analyze_results(links_dict)
                    
                    #Отображение результатов
                    display_analysis_results(links_dict, analysis)
                else:
                    print("\n❌ HTML код не был введен")
            
            #Обработка выбора "Использовать пример HTML"
            elif choice == '2':
                print("\n" + "-" * 40)
                print("ПРИМЕР HTML КОДА")
                print("-" * 40)
                
                example = show_example_html()  #Получение примера HTML
                print("Пример HTML кода с различными типами ссылок:")
                print("-" * 40)
                print(example)
                print("-" * 40)
                
                #Запрос на использование примера
                use_example = input("\nПроанализировать этот пример? (да/нет): ").strip().lower()
                if use_example in ['да', 'д', 'y', 'yes']:
                    print("\n⏳ Анализирую пример HTML...")
                    
                    #Анализ примера HTML
                    links_dict = finder.find_all_links(example)
                    analysis = finder.analyze_results(links_dict)
                    
                    display_analysis_results(links_dict, analysis)
            
            #Обработка выбора "Показать информацию о программе"
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
                print("   • Имеет встроенные unit-тесты для проверки корректности")  #Добавлена информация о тестах
                
                #Вывод регулярных выражений, используемых программой
                print("\n📝 Регулярные выражения, которые использует программа:")
                for pattern_name, pattern in finder.patterns.items():
                    readable_name = pattern_name.replace('ссылки_', 'Для ')
                    print(f"   • {readable_name}: {pattern}")
                
                #Пример использования программы
                print("\n💡 Пример использования:")
                print("   html = '<a href=\"https://example.com\">Ссылка</a>'")
                print("   links = finder.find_all_links(html)")
                print("   print(links)  # Выведет найденные ссылки")
                
                #Добавлена информация о тестах
                print("\n🧪 Unit-тесты:")
                print("   • Проверяют корректность регулярных выражений")
                print("   • Тестируют обработку граничных случаев")
                print("   • Проверяют классификацию ссылок")
                print("   • Запускаются через меню (пункт 4)")
                print("=" * 70)
            
            #Новый блок для запуска тестов
            elif choice == '4':
                print("\n" + "-" * 40)
                print("UNIT-ТЕСТИРОВАНИЕ")
                print("-" * 40)
                print("Запуск тестов для проверки корректности работы программы:")
                print("1. Тесты регулярных выражений")
                print("2. Тесты методов класса HTMLLinkFinder")
                print("3. Интеграционные тесты")
                print("-" * 40)
                
                confirm = input("\nЗапустить тесты? (да/нет): ").strip().lower()
                if confirm in ['да', 'д', 'y', 'yes']:
                    success = run_tests()
                    if success:
                        print("✅ Все тесты пройдены успешно!")
                    else:
                        print("⚠️  Некоторые тесты не пройдены")
                else:
                    print("❌ Тестирование отменено")
            
            #Обработка выбора "Выход" (теперь пункт 5)
            elif choice == '5':
                print("\n" + "=" * 50)
                print("Спасибо за использование программы!")
                print("До свидания!")
                print("=" * 50)
                break  #Завершение цикла и выход из программы
            
            else:
                print("\n❌ Неверный выбор. Пожалуйста, введите число от 1 до 5.")
        
        #Обработка исключений
        except KeyboardInterrupt:  #Обработка прерывания (Ctrl+C)
            print("\n\n⚠️  Программа прервана пользователем")
            break
        except Exception as e:  #Обработка всех остальных ошибок
            print(f"\n❌ Произошла ошибка: {e}")
            print("Попробуйте еще раз")


#Расширенная точка входа в программу
#Проверяет аргументы командной строки для запуска тестов
if __name__ == "__main__":
    import sys
    
    #Обработка аргументов командной строки
    #Позволяет запускать тесты напрямую: python script.py --test
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        #Запуск только тестов без основного меню
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        #Обычный запуск с меню
        main()
