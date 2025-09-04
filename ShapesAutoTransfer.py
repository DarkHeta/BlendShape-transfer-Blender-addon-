bl_info = {
    "name": "BlendShape Transfer",
    "author": "Heta",
    "version": (1, 3, 0),
    "blender": (2, 80, 0),
    "location": "View3D > N Panel > BlendShape Transfer",
    "description": "Transfer blend shapes from source to target object",
    "category": "Object",
}

import bpy

class BlendShapeProperties(bpy.types.PropertyGroup):
    source_object: bpy.props.PointerProperty(
        name="Source Object",
        description="Object with blend shapes to transfer from",
        type=bpy.types.Object
    )
    
    show_blendshapes: bpy.props.BoolProperty(
        name="Show BlendShapes",
        description="Show/Hide the list of blend shapes",
        default=False
    )

class BLENDSHAPE_OT_transfer(bpy.types.Operator):
    """Transfer blend shapes from source to selected object"""
    bl_idname = "blendshape.transfer"
    bl_label = "Transfer BlendShapes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        blendshape_tool = scene.blendshape_tool
        
        # Получаем объект-источник
        body_object = blendshape_tool.source_object
        if not body_object:
            self.report({'ERROR'}, "Source object is not set")
            return {'CANCELLED'}
        
        # Получаем выделенный объект-цель
        target_object = context.active_object
        if not target_object:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        if body_object == target_object:
            self.report({'ERROR'}, "Source and target objects cannot be the same")
            return {'CANCELLED'}
        
        # Проверяем наличие блендшейпов у тела
        if not body_object.data.shape_keys or not body_object.data.shape_keys.key_blocks:
            self.report({'ERROR'}, f"No shape keys found on {body_object.name}")
            return {'CANCELLED'}
        
        # Сохраняем исходное состояние блендшейпов тела
        original_active_index = body_object.active_shape_key_index
        original_values = {key.name: key.value for key in body_object.data.shape_keys.key_blocks}
        
        # Создаем словарь для хранения исходных значений целевого объекта
        target_original_values = {}
        if target_object.data.shape_keys:
            target_original_values = {key.name: key.value for key in target_object.data.shape_keys.key_blocks}
        
        # Цикл по всем блендшейпам тела (начиная с первого, пропускаем базовый Basis)
        blendshapes = body_object.data.shape_keys.key_blocks
        for idx, blendshape in enumerate(blendshapes):
            if idx == 0:
                continue  # Пропускаем базовый шейп Basis
            
            # Устанавливаем текущий блендшейп активным на теле
            body_object.active_shape_key_index = idx
            
            # Добавляем модификатор Surface Deform к целевому объекту
            mod_name = f"SurfaceDeform_{blendshape.name}"
            modifier = target_object.modifiers.new(name=mod_name, type='SURFACE_DEFORM')
            modifier.target = body_object
            modifier.falloff = 1.0
            modifier.strength = 1.0
            
            # Активируем целевой объект для привязки модификатора 
            original_active = context.view_layer.objects.active
            context.view_layer.objects.active = target_object
            
            # Привязываем модификатор 
            bpy.ops.object.surfacedeform_bind(modifier=mod_name)
            
            # Устанавливаем значение блендшейпа на теле в 1.0
            blendshape.value = 1.0
            
            # Обновляем сцену для применения изменений 
            context.view_layer.update()
            
            # Применяем модификатор как форму
            try:
                # Для новых версий Blender
                bpy.ops.object.modifier_apply_as_shapekey(modifier=mod_name)
            except:
                # Для старых версий
                try:
                    bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod_name)
                except:
                    # Если оба метода не работают, просто удаляем модификатор
                    target_object.modifiers.remove(modifier)
            
            # Возвращаем исходный активный объект
            context.view_layer.objects.active = original_active
            
            # Переименовываем новый шейп на целевом объекте 
            if target_object.data.shape_keys and len(target_object.data.shape_keys.key_blocks) > 0:
                new_shape_key = target_object.data.shape_keys.key_blocks[-1]
                new_shape_key.name = blendshape.name
            
            # Возвращаем значение блендшейпа на теле к исходному
            blendshape.value = 0.0
        
        # Восстанавливаем исходные значения блендшейпов тела
        for key in body_object.data.shape_keys.key_blocks:
            if key.name in original_values:
                key.value = original_values[key.name]
        body_object.active_shape_key_index = original_active_index
        
        # Восстанавливаем исходные значения блендшейпов целевого объекта
        if target_object.data.shape_keys:
            for key in target_object.data.shape_keys.key_blocks:
                if key.name in target_original_values:
                    key.value = target_original_values[key.name]
        
        self.report({'INFO'}, f"Blend shapes transferred from {body_object.name} to {target_object.name}")
        return {'FINISHED'}

class BLENDSHAPE_PT_panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport"""
    bl_label = "BlendShape Transfer Pro"
    bl_idname = "BLENDSHAPE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BlendShape Transfer"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        blendshape_tool = scene.blendshape_tool
        source_obj = blendshape_tool.source_object
        
        # Поле выбора объекта (без пипетки)
        layout.prop_search(blendshape_tool, "source_object", scene, "objects", 
                          text="Source Object", icon='OBJECT_DATA')
        
        # Выпадающий список блендшейпов с фиксированным размером и прокруткой
        if source_obj and source_obj.data.shape_keys:
            box = layout.box()
            row = box.row()
            row.prop(blendshape_tool, "show_blendshapes", 
                    text="BlendShapes", 
                    icon='TRIA_DOWN' if blendshape_tool.show_blendshapes else 'TRIA_RIGHT',
                    emboss=False)
            
            if blendshape_tool.show_blendshapes:
                blendshapes = source_obj.data.shape_keys.key_blocks
                
                # Создаем область с фиксированной высотой и прокруткой
                scroll_box = box.box()
                scroll_box.scale_y = 0.8  # Уменьшаем высоту области
                
                # Ограничиваем количество отображаемых элементов
                max_display_items = 10
                display_count = min(len(blendshapes) - 1, max_display_items)  # -1 чтобы исключить Basis
                
                # Отображаем блендшейпы (пропускаем Basis)
                for i, shape_key in enumerate(blendshapes):
                    if i == 0:  # Пропускаем Basis
                        continue
                    
                    # Пропускаем элементы за пределами видимой области
                    if i - 1 >= max_display_items:
                        continue
                    
                    row = scroll_box.row()
                    row.enabled = False  # Делаем некликабельным
                    row.label(text=shape_key.name, icon='SHAPEKEY_DATA')
                
                # Добавляем информацию о количестве блендшейпов
                if len(blendshapes) - 1 > max_display_items:
                    row = box.row()
                    row.alignment = 'CENTER'
                    row.label(text=f"... and {len(blendshapes) - 1 - max_display_items} more", icon='DOT')
        
        # Кнопка применения
        layout.separator()
        layout.operator("blendshape.transfer", text="Apply BlendShapes", icon='COPYDOWN')

classes = (
    BlendShapeProperties,
    BLENDSHAPE_OT_transfer,
    BLENDSHAPE_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.blendshape_tool = bpy.props.PointerProperty(type=BlendShapeProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.blendshape_tool

if __name__ == "__main__":
    register()