bl_info = {
	"name": "Pose Sketch (iffy)",
	"author": "Ed-eX",
	#"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "View 3D",
	#"description": "Collection of Scripts",
	"warning": "check script first",
	#"wiki_url" : "",
	#"tracker_url" : "",
	"category": " Custom"}
##############################
import bpy, mathutils, fnmatch
from mathutils import Vector
on = True;	off = False;
##############################
def KeyframeConstraint(value,round, apply,toggle,usevalue,keyframe,keyingset):
	if bpy.context.mode == 'POSE':
		src = bpy.context.selected_pose_bones;	srctype = "Bone";
		if apply == on:	bpy.ops.pose.visual_transform_apply();
	elif bpy.context.mode == 'OBJECT':
		src = bpy.context.selected_objects;	srctype = "Object";
		if apply == on:	bpy.ops.object.visual_transform_apply();
	else:	src = "null";
	if src != "null":
		for target in src:
			for constraint in target.constraints:
				if round==on:
					if constraint.influence <= 0.225:	newvalue = 0;
					elif constraint.influence >= 0.775:	newvalue = 1;
					else:	newvalue = 0.5;
				if usevalue==on:
					if value == -1:	newvalue = constraint.influence;
					else:	newvalue = value;
					constraint.influence = newvalue;
				if toggle==on:
					if constraint.mute == True:	constraint.mute = False;
					elif constraint.mute == False:	constraint.mute = True;
					#refresh << lag
					#if keyingset == 'off':	bpy.context.scene.frame_set(bpy.context.scene.frame_current, bpy.context.scene.frame_current_final-bpy.context.scene.frame_current);
				if keyframe==on:
					constraint.keyframe_insert(data_path="influence", group=srctype+" Constraints", options={'INSERTKEY_NEEDED'});
					'''for obj in bpy.context.selected_objects:
						if obj.animation_data:
							for curve in obj.animation_data.action.groups[srctype+' Constraints'].id_data.fcurves:
								for key in curve.keyframe_points:
									key.interpolation = 'CONSTANT'; '''
		if keyingset != off:
			if apply == on and srctype == "Bone":	bpy.ops.pose.visual_transform_apply();
			if apply == on and srctype == "Object":	bpy.ops.object.visual_transform_apply();
			#keyingsets fixes
			if bpy.context.scene.keying_sets.active:	keyingsetfix = bpy.context.scene.keying_sets.active.type_info.bl_idname;
			elif not bpy.context.scene.keying_sets.active:	keyingsetfix = 'LocRotScale';
			if srctype == "Bone" and keyingsetfix in('Location', 'Rotation', 'Scale', 'LocRotScale', 'BUILTIN_KSI_LocRot', 'BUILTIN_KSI_RotScale', 'BUILTIN_KSI_LocScale'):
				if keyingsetfix == 'Location':	keyingsetfix = 'BUILTIN_KSI_VisualLoc';
				elif keyingsetfix == 'Rotation':	keyingsetfix = 'BUILTIN_KSI_VisualRot';
				elif keyingsetfix == 'BUILTIN_KSI_LocRot':	keyingsetfix = 'BUILTIN_KSI_VisualLocRot';
				elif keyingsetfix == 'BUILTIN_KSI_RotScale':	keyingsetfix = 'BUILTIN_KSI_VisualRotScale';
				elif keyingsetfix == 'BUILTIN_KSI_LocScale':	keyingsetfix = 'BUILTIN_KSI_VisualLocScale';
				else:	keyingsetfix = 'BUILTIN_KSI_Visual'+keyingsetfix;
			bpy.ops.anim.keyframe_insert_menu(type=keyingsetfix);
			if toggle==on:
				for target in src:
					for constraint in target.constraints:
						if constraint.mute == True:	constraint.mute = False;
						elif constraint.mute == False:	constraint.mute = True;
		#refresh
		if toggle==on:	bpy.context.scene.frame_set(bpy.context.scene.frame_current, bpy.context.scene.frame_current_final-bpy.context.scene.frame_current);

def PoseSketch():
	'''
	wintype = "VIEW_3D"
	if bpy.context.space_data.type != "VIEW_3D":
		wintype = bpy.context.space_data.type
		bpy.ops.wm.context_set_enum(data_path="area.type", value= "VIEW_3D")
	'''
	bpy.context.tool_settings.use_gpencil_continuous_drawing = False
	if bpy.context.space_data.type == "VIEW_3D" and bpy.context.active_object.type == 'ARMATURE':
		if bpy.context.mode in ('OBJECT','POSE'):
		#if 1==1:
		#	bpy.ops.object.mode_set(mode='GPENCIL_EDIT') #not needed
		#	bpy.ops.object.mode_set(mode='POSE')
		#if bpy.context.mode == 'POSE':
			#if bpy.context.mode == 'GPENCIL_EDIT'
			bpy.ops.object.mode_set(mode='POSE')
			armature = bpy.context.active_object
			bones = bpy.context.selected_pose_bones
			bonecount = len(bones)

			if bonecount > 0  #prevent error when no bone is selected
				if bpy.context.scene.cursor_location != bones[0].head:
					bpy.context.scene.cursor_location = bones[0].head
					#bpy.ops.gpencil.active_frames_delete_all()

				else:
					if str(bpy.context.scene.grease_pencil.layers.active.active_frame) != 'None':
					#bpy.context.scene.grease_pencil.layers.active.active_frame.strokes
					#len(bpy.data.grease_pencil['GPencil'].layers['GP_Layer'].active_frame.strokes)

						GreasePencil = bpy.context.scene.grease_pencil.layers.active.info
						bpy.context.scene.grease_pencil.layers.active.info = "PoseSketch"
						gpname = bpy.context.scene.grease_pencil.layers.active.info

						#convert grease then delete
						bpy.ops.gpencil.convert(type='PATH', use_timing_data=False)
						bpy.ops.gpencil.active_frames_delete_all()

						#select curve
						bpy.context.scene.objects.active = bpy.context.scene.objects[gpname]
						bpy.ops.object.select_pattern(pattern=gpname, extend=False)

						#points = bpy.context.active_object.data.splines[0].point_count_u
						splines = bpy.data.curves[gpname].splines
						splinecount = len(splines)-1

						points = bpy.data.curves[gpname].splines[splinecount].point_count_u
						point_0 = 0
						point_10 = round(points*.1)-1
						point_15 = round(points*.15)-1
						point_20 = round(points*.2)-1
						point_25 = round(points*.25)-1
						point_30 = round(points*.3)-1
						point_33 = round(points*.333)-1
						point_40 = round(points*.4)-1
						point_50 = round(points*.5)-1
						point_60 = round(points*.6)-1
						point_66 = round(points*.666)-1
						point_70 = round(points*.7)-1
						point_75 = round(points*.75)-1
						point_80 = round(points*.8)-1
						point_85 = round(points*.85)-1
						point_90 = round(points*.9)-1
						point_100 = points-1

						#Vector((X,Y,Z,W)) <to> Vector((X,Y,Z))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_0].co
						loc_0 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_10].co
						loc_10 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_15].co
						loc_15 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_20].co
						loc_20 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_25].co
						loc_25 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_30].co
						loc_30 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_33].co
						loc_33 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_40].co
						loc_40 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_50].co
						loc_50 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_60].co
						loc_60 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_66].co
						loc_66 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_70].co
						loc_70 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_75].co
						loc_75 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_80].co
						loc_80 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_85].co
						loc_85 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_90].co
						loc_90 = Vector((pointloc[0],pointloc[1],pointloc[2]))
						pointloc = bpy.data.curves[gpname].splines[0].points[point_100].co
						loc_100 = Vector((pointloc[0],pointloc[1],pointloc[2]))

						#Delete curve
						bpy.context.active_object.data.name+='.delete'
						bpy.ops.object.delete(use_global=True)
						

						if bonecount != 0:
							bpy.ops.object.empty_add(radius=.1,location=loc_0)
							target_0 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_10)
							target_10 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_15)
							target_15 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_20)
							target_20 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_25)
							target_25 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_30)
							target_30 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_33)
							target_33 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_40)
							target_40 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_50)
							target_50 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_60)
							target_60 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_66)
							target_66 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_70)
							target_70 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_75)
							target_75 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_80)
							target_80 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_85)
							target_85 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_90)
							target_90 = bpy.context.active_object
							bpy.ops.object.empty_add(radius=.1,location=loc_100)
							target_100 = bpy.context.active_object
							

						bpy.context.scene.objects.active = armature
						#for bone in bones:

						stretch = True
						useloc = True
						def boneCon(Target0, Bone,Target,Stretch,useloc):
							armature = bpy.context.active_object
							armature.data.bones.active = Bone.bone
							#location change for some bones
							if useloc and (not Bone.parent or Bone.name in ("spine", "pelvis", "bone")):
								bpy.ops.pose.constraint_add(type='COPY_LOCATION')
								constraints = bpy.context.active_pose_bone.constraints
								constraint = constraints[len(constraints)-1]
								constraint.target = Target0
								constraint.use_x = not Bone.lock_location[0]
								constraint.use_y = not Bone.lock_location[1]
								constraint.use_z = not Bone.lock_location[2]

								bpy.ops.pose.visual_transform_apply()
								############## custom keyframe operator	[value,round, apply,toggle,usevalue,keyframe,keyingset]
								KeyframeConstraint(-1, 0, 1, 1,0,0,1)
								constraints.remove(constraint)
							#bpy.ops.object.select_pattern(pattern=Bone.name, extend=False)
							bpy.ops.pose.constraint_add(type='IK')
							constraints = bpy.context.active_pose_bone.constraints
							constraint = constraints[len(constraints)-1]
							constraint.chain_count = 1
							constraint.use_stretch = Stretch#+ (not Bone.lock_scale[0]+ not Bone.lock_scale[1]+ not Bone.lock_scale[2])/3
							constraint.target = Target
							'''
							#reset bone twist/
							bpy.ops.pose.constraint_add(type='COPY_ROTATION')
							constraint = constraints[len(constraints)-1]
							constraint.target = Target
							constraint.target_space = 'LOCAL'
							constraint.owner_space = 'LOCAL'
							#/reset
							'''
							bpy.ops.pose.visual_transform_apply()
							############## custom keyframe operator	[value,round, apply,toggle,usevalue,keyframe,keyingset]
							KeyframeConstraint(-1, 0, 1, 1,0,0, 1)
							constraints.remove(constraints[len(constraints)-1])
							#constraints.remove(constraints[len(constraints)-1])
						if bonecount == 1:
							boneCon(target_0, bones[0],target_100,stretch,useloc)
						if bonecount == 2:
							boneCon(target_0, bones[0],target_50,stretch,useloc)
							boneCon(target_50, bones[1],target_100,stretch,useloc)
						if bonecount == 3:
							boneCon(target_0, bones[0],target_33,stretch,useloc)
							boneCon(target_33, bones[1],target_66,stretch,useloc)
							boneCon(target_66, bones[2],target_100,stretch,useloc)
						if bonecount == 4:
							boneCon(target_0, bones[0],target_25,stretch,useloc)
							boneCon(target_25, bones[1],target_50,stretch,useloc)
							boneCon(target_50, bones[2],target_75,stretch,useloc)
							boneCon(target_75, bones[3],target_100,stretch,useloc)
						if bonecount == 5:
							boneCon(target_0, bones[0],target_20,stretch,useloc)
							boneCon(target_20, bones[1],target_40,stretch,useloc)
							boneCon(target_40, bones[2],target_60,stretch,useloc)
							boneCon(target_60, bones[3],target_80,stretch,useloc)
							boneCon(target_80, bones[4],target_100,stretch,useloc)
						if bonecount == 6:
							boneCon(target_0, bones[0],target_15,stretch,useloc)
							boneCon(target_15, bones[1],target_33,stretch,useloc)
							boneCon(target_33, bones[2],target_50,stretch,useloc)
							boneCon(target_50, bones[3],target_66,stretch,useloc)
							boneCon(target_66, bones[4],target_85,stretch,useloc)
							boneCon(target_85, bones[5],target_100,stretch,useloc)
						if bonecount == 7:
							boneCon(target_0, bones[0],target_15,stretch,useloc)
							boneCon(target_15, bones[1],target_30,stretch,useloc)
							boneCon(target_30, bones[2],target_40,stretch,useloc)
							boneCon(target_40, bones[3],target_60,stretch,useloc)
							boneCon(target_60, bones[4],target_70,stretch,useloc)
							boneCon(target_70, bones[5],target_85,stretch,useloc)
							boneCon(target_85, bones[6],target_100,stretch,useloc)
						if bonecount == 8:
							boneCon(target_0, bones[0],target_15,stretch,useloc)
							boneCon(target_15, bones[1],target_25,stretch,useloc)
							boneCon(target_25, bones[2],target_33,stretch,useloc)
							boneCon(target_33, bones[3],target_50,stretch,useloc)
							boneCon(target_50, bones[4],target_66,stretch,useloc)
							boneCon(target_66, bones[5],target_75,stretch,useloc)
							boneCon(target_75, bones[6],target_85,stretch,useloc)
							boneCon(target_85, bones[7],target_100,stretch,useloc)
						if bonecount == 9:
							boneCon(target_0, bones[0],target_10,stretch,useloc)
							boneCon(target_10, bones[1],target_20,stretch,useloc)
							boneCon(target_20, bones[2],target_33,stretch,useloc)
							boneCon(target_33, bones[3],target_40,stretch,useloc)
							boneCon(target_40, bones[4],target_50,stretch,useloc)
							boneCon(target_50, bones[5],target_66,stretch,useloc)
							boneCon(target_66, bones[6],target_75,stretch,useloc)
							boneCon(target_75, bones[7],target_85,stretch,useloc)
							boneCon(target_85, bones[8],target_100,stretch,useloc)
						if bonecount == 10:
							boneCon(target_0, bones[0],target_10,stretch,useloc)
							boneCon(target_10, bones[1],target_20,stretch,useloc)
							boneCon(target_20, bones[2],target_30,stretch,useloc)
							boneCon(target_30, bones[3],target_40,stretch,useloc)
							boneCon(target_40, bones[4],target_50,stretch,useloc)
							boneCon(target_50, bones[5],target_60,stretch,useloc)
							boneCon(target_60, bones[6],target_70,stretch,useloc)
							boneCon(target_70, bones[7],target_80,stretch,useloc)
							boneCon(target_80, bones[8],target_90,stretch,useloc)
							boneCon(target_90, bones[9],target_100,stretch,useloc)
						bpy.context.scene.objects.active = target_0
						bpy.ops.object.select_pattern(pattern=target_0.name, extend=False)
						bpy.ops.object.select_pattern(pattern=target_10.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_15.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_20.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_25.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_30.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_33.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_40.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_50.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_60.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_66.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_70.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_75.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_80.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_85.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_90.name, extend=True)
						bpy.ops.object.select_pattern(pattern=target_100.name, extend=True)
						bpy.ops.object.delete(use_global=True)
						bpy.context.scene.objects.active = armature


						bpy.context.scene.grease_pencil.layers.active.info = GreasePencil
						bpy.context.scene.cursor_location = bones[0].head

	'''bpy.context.space_data.type == wintype
	bpy.ops.wm.context_set_enum(data_path="area.type", value=wintype ) 
	'''
	#Scrap / Doodles down here:


	'''
			def boneLoc(Bone,Target):
				if Bone.name in ("spine"):
					armature = bpy.context.active_object
					armature.data.bones.active = Bone.bone
					bpy.ops.pose.constraint_add(type='COPY_LOCATION')
					constraints = bpy.context.active_pose_bone.constraints
					constraint = constraints[len(constraints)-1]
					constraint.target = Target
					bpy.ops.pose.visual_transform_apply()
					bpy.ops.z.constraint_keyframes(value=-1, apply = 1, toggle = 1, round=0,usevalue=0,keyframe=0, keyingset=1)
					constraints.remove(constraint)
			def boneCon(Bone,Target):
				armature = bpy.context.active_object
				armature.data.bones.active = Bone.bone
				#bpy.ops.object.select_pattern(pattern=Bone.name, extend=False)
				bpy.ops.pose.constraint_add(type='IK')
				constraints = bpy.context.active_pose_bone.constraints
				constraint = constraints[len(constraints)-1]
				constraint.chain_count = 1
				constraint.target = Target
				bpy.ops.pose.visual_transform_apply()
				bpy.ops.z.constraint_keyframes(value=-1, apply = 1, toggle = 1, round=0,usevalue=0,keyframe=0, keyingset=1)
				constraints.remove(constraint)
			def boneRest(Bone,Target):
				armature = bpy.context.active_object
				armature.data.bones.active = Bone.bone
				bpy.ops.pose.constraint_add(type='COPY_ROTATION')
				constraints = bpy.context.active_pose_bone.constraints
				constraint = constraints[len(constraints)-1]
				constraint.target = Target
				constraint.target_space = 'LOCAL'
				constraint.owner_space = 'LOCAL'
				bpy.ops.pose.visual_transform_apply()
				bpy.ops.z.constraint_keyframes(value=-1, apply = 1, toggle = 1, round=0,usevalue=0,keyframe=0, keyingset=1)
				constraints.remove(constraint)
				'''

class poseSketch(bpy.types.Operator):
	bl_label = "Grease Pencil Pose Sketch";	bl_idname = "pose.posesketch";	
	bl_description = "Fit selected bones to Grease Pencil Stroke";
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self,context):	PoseSketch();	return {'FINISHED'};

class PoseSketch_Header(bpy.types.Header):
	bl_space_type = "VIEW_3D";	bl_region_type = "HEADER";	#bl_context = 'constraint'
	
	def draw(self, context):	
		layout = self.layout;	scene = context.scene;	object = context.object;	
		row = layout.row(align=True);	
		row.operator('pose.posesketch',text='',icon='POSE_DATA');
		
	
def register():	bpy.utils.register_module(__name__);	
def unregister():	bpy.utils.unregister_module(__name__);	
if __name__ == "__main__":	register();
