#!/usr/bin/env python3
"""
IFC Files Merger with Color Priority

A tool for merging multiple IFC files while preserving color schemes and material properties.

Original concept and initial implementation: Google Gemini (at request of Ivan Rodionov)
Material handling improvements and color preservation: Claude (Anthropic)
Project initiated by: Ivan Rodionov

This script merges multiple IFC files into a single file, giving priority to the color scheme
and material properties of the first (base) file. It handles various IFC color definitions
including materials, surface styles, styled items, and their relationships.

Usage:
    python ifc_merger.py <output_file.ifc> <base_file.ifc> <file2.ifc> [file3.ifc ...]
    python ifc_merger.py --analyze <file.ifc>

Features:
    - Preserves color schemes from the base file
    - Handles material relationships and styled items
    - Provides diagnostic tools for color analysis
    - Robust error handling and conflict resolution

Requirements:
    - ifcopenshell library (install with: pip install ifcopenshell)
    - Python 3.6+

License: MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import ifcopenshell
import sys
import os

def merge_ifc_files_with_color_priority(input_files, output_file):
    """
    Объединяет несколько IFC-файлов в один, отдавая приоритет цветовой схеме
    первого входного файла с улучшенным сохранением цветовой информации.

    Args:
        input_files (list): Список путей к исходным IFC-файлам. Первый файл
                             считается основным для цветовой схемы.
        output_file (str): Путь к файлу, в который будет записан объединенный результат.
    """
    if not input_files:
        print("Ошибка: Не указаны входные файлы для объединения.")
        return

    # 1. Загружаем первый файл и делаем его основой
    try:
        base_model_path = input_files[0]
        if not os.path.exists(base_model_path):
            print(f"Ошибка: Основной файл не найден: {base_model_path}")
            sys.exit(1)

        base_model = ifcopenshell.open(base_model_path)
        merged_model = ifcopenshell.file(schema=base_model.schema)
        print(f"Используется схема IFC: {base_model.schema} (из {base_model_path})")

        # Добавляем все сущности из первого файла в объединенную модель
        print(f"Обрабатывается основной файл: {base_model_path} ({len(base_model.by_type('IfcProduct'))} IfcProducts)")
        
        # Копируем ВСЕ сущности из основного файла, включая все цветовые определения
        for entity in base_model:
            try:
                merged_model.add(entity)
            except Exception as e:
                print(f"  Предупреждение: Не удалось добавить сущность {entity} из основного файла: {e}")

        # Создаем наборы для отслеживания уже добавленных цветовых элементов
        known_materials = {m.Name.lower() for m in base_model.by_type("IfcMaterial") if m.Name}
        known_surface_styles = {s.Name.lower() for s in base_model.by_type("IfcSurfaceStyle") if s.Name}
        known_styled_items = {item.id() for item in base_model.by_type("IfcStyledItem")}
        known_colours = {colour.id() for colour in base_model.by_type("IfcColourRgb")}
        known_presentation_styles = {style.id() for style in base_model.by_type("IfcPresentationStyleAssignment")}

    except Exception as e:
        print(f"Критическая ошибка: Не удалось открыть или обработать основной файл ({input_files[0]}). Убедитесь, что он корректен.")
        print(f"Детали ошибки: {e}")
        sys.exit(1)

    # 2. Обрабатываем остальные файлы
    for i, file_path in enumerate(input_files[1:], 1):
        if not os.path.exists(file_path):
            print(f"Предупреждение: Файл не найден и будет пропущен: {file_path}")
            continue

        try:
            current_model = ifcopenshell.open(file_path)
            print(f"Обрабатывается дополнительный файл: {file_path} ({len(current_model.by_type('IfcProduct'))} IfcProducts)")

            # Сначала добавляем все цветовые определения, которых еще нет
            
            # 1. Добавляем новые цвета
            for colour in current_model.by_type("IfcColourRgb"):
                if colour.id() not in known_colours:
                    try:
                        merged_model.add(colour)
                        known_colours.add(colour.id())
                    except:
                        pass

            # 2. Добавляем новые стили презентации
            for style in current_model.by_type("IfcPresentationStyleAssignment"):
                if style.id() not in known_presentation_styles:
                    try:
                        merged_model.add(style)
                        known_presentation_styles.add(style.id())
                    except:
                        pass

            # 3. Добавляем новые поверхностные стили (только если имя не конфликтует)
            for surface_style in current_model.by_type("IfcSurfaceStyle"):
                style_name = surface_style.Name.lower() if surface_style.Name else f"unnamed_{surface_style.id()}"
                if style_name not in known_surface_styles:
                    try:
                        merged_model.add(surface_style)
                        known_surface_styles.add(style_name)
                    except:
                        pass

            # 4. Добавляем новые материалы (только если имя не конфликтует)
            for material in current_model.by_type("IfcMaterial"):
                material_name = material.Name.lower() if material.Name else f"unnamed_{material.id()}"
                if material_name not in known_materials:
                    try:
                        merged_model.add(material)
                        known_materials.add(material_name)
                    except:
                        pass

            # 5. Добавляем новые стилизованные элементы
            for styled_item in current_model.by_type("IfcStyledItem"):
                if styled_item.id() not in known_styled_items:
                    try:
                        merged_model.add(styled_item)
                        known_styled_items.add(styled_item.id())
                    except:
                        pass

            # 6. Добавляем связи материалов с элементами
            for material_relation in current_model.by_type("IfcRelAssociatesMaterial"):
                try:
                    merged_model.add(material_relation)
                except:
                    pass

            # 7. Добавляем слои презентации
            for layer in current_model.by_type("IfcPresentationLayerAssignment"):
                try:
                    merged_model.add(layer)
                except:
                    pass

            # 8. Теперь добавляем все остальные сущности
            for entity in current_model:
                # Пропускаем уже обработанные типы цветовых элементов
                if entity.is_a() in ["IfcColourRgb", "IfcPresentationStyleAssignment", 
                                   "IfcSurfaceStyle", "IfcMaterial", "IfcStyledItem",
                                   "IfcRelAssociatesMaterial", "IfcPresentationLayerAssignment"]:
                    continue
                
                try:
                    merged_model.add(entity)
                except Exception as add_e:
                    # Обрабатываем возможные ошибки при добавлении
                    if hasattr(entity, 'Name') and entity.Name:
                        print(f"  Предупреждение: Не удалось добавить сущность {entity.Name} ({entity.id()}) из {file_path}. Возможно, дубликат или конфликт.")
                    elif hasattr(entity, 'GlobalId'):
                        print(f"  Предупреждение: Не удалось добавить сущность с GlobalId {entity.GlobalId} из {file_path}.")

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}. Файл будет пропущен.")

    try:
        # Сохраняем объединенную модель
        merged_model.write(output_file)
        print(f"\nУспешно объединено в: {output_file}")
        print(f"Общее количество IfcProducts в объединенной модели: {len(merged_model.by_type('IfcProduct'))}")
        print(f"Общее количество материалов: {len(merged_model.by_type('IfcMaterial'))}")
        print(f"Общее количество стилей поверхности: {len(merged_model.by_type('IfcSurfaceStyle'))}")
        print(f"Общее количество стилизованных элементов: {len(merged_model.by_type('IfcStyledItem'))}")
        
    except Exception as e:
        print(f"\nОшибка при записи объединенного файла {output_file}: {e}")

def validate_ifc_colors(ifc_file):
    """
    Вспомогательная функция для анализа цветовой информации в IFC файле
    """
    print(f"\n=== Анализ цветовой информации в {ifc_file} ===")
    try:
        model = ifcopenshell.open(ifc_file)
        
        materials = model.by_type("IfcMaterial")
        print(f"Материалы: {len(materials)}")
        for mat in materials[:5]:  # Показываем первые 5
            print(f"  - {mat.Name if mat.Name else 'Unnamed'}")
        
        surface_styles = model.by_type("IfcSurfaceStyle")
        print(f"Стили поверхности: {len(surface_styles)}")
        for style in surface_styles[:5]:
            print(f"  - {style.Name if style.Name else 'Unnamed'}")
        
        styled_items = model.by_type("IfcStyledItem")
        print(f"Стилизованные элементы: {len(styled_items)}")
        
        colours = model.by_type("IfcColourRgb")
        print(f"RGB цвета: {len(colours)}")
        for colour in colours[:3]:
            print(f"  - RGB({colour.Red:.3f}, {colour.Green:.3f}, {colour.Blue:.3f})")
        
        material_relations = model.by_type("IfcRelAssociatesMaterial")
        print(f"Связи материалов: {len(material_relations)}")
        
    except Exception as e:
        print(f"Ошибка при анализе файла: {e}")

if __name__ == "__main__":
    # Usage:
    # python ifc_merger.py <output_file.ifc> <base_file.ifc> <file2.ifc> [file3.ifc ...]
    # python ifc_merger.py --analyze <file.ifc>  # for color analysis

    if len(sys.argv) >= 3 and sys.argv[1] == "--analyze":
        validate_ifc_colors(sys.argv[2])
        sys.exit(0)

    if len(sys.argv) < 3:
        print("IFC Files Merger with Color Priority")
        print("Original concept: Google Gemini | Material improvements: Claude | Initiated by: Ivan Rodionov")
        print("")
        print("Requirements: pip install ifcopenshell")
        print("")
        print("Usage:")
        print("  python ifc_merger.py <output_file.ifc> <base_file.ifc> <file2.ifc> [file3.ifc ...]")
        print("  python ifc_merger.py --analyze <file.ifc>")
        print("")
        print("The first file in the list (after output) will be used as the base for color scheme.")
        sys.exit(1)

    output_ifc = sys.argv[1]
    input_ifc_files = sys.argv[2:]

    print("IFC Files Merger with Color Priority")
    print("Original concept: Google Gemini | Material improvements: Claude | Initiated by: Ivan Rodionov")
    print("=" * 80)

    # Analyze source file before merging
    print("=== Analysis of source file ===")
    validate_ifc_colors(input_ifc_files[0])

    merge_ifc_files_with_color_priority(input_ifc_files, output_ifc)
    
    # Analyze result
    print("\n=== Analysis of result ===")
    validate_ifc_colors(output_ifc)