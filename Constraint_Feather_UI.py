from maya import cmds as mc

def uniform_twist_ui():
    win_name = "uniformTwistUI"
    if mc.window(win_name, exists=True):
        mc.deleteUI(win_name)

    mc.window(win_name, title="Uniform Twist / Point Constraint Tool", widthHeight=(400, 250))
    mc.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center")

    # Instructions
    mc.text(label="Select objects in order: First -> Middle(s) -> Last")
    
    # Buttons to populate fields
    mc.text(label="First Object:")
    first_obj_field = mc.textFieldButtonGrp('firstObj', buttonLabel='Get Selected', text='')
    mc.text(label="Last Object:")
    last_obj_field = mc.textFieldButtonGrp('lastObj', buttonLabel='Get Selected', text='')
    mc.text(label="In-Between Objects (multiple):")
    middle_objs_field = mc.textFieldButtonGrp('middleObjs', buttonLabel='Get Selected', text='')

    def get_first_selected(*args):
        sel = mc.ls(sl=True)
        if sel:
            mc.textFieldButtonGrp(first_obj_field, edit=True, text=sel[0])
        else:
            mc.warning("No object selected!")

    def get_last_selected(*args):
        sel = mc.ls(sl=True)
        if sel:
            mc.textFieldButtonGrp(last_obj_field, edit=True, text=sel[0])
        else:
            mc.warning("No object selected!")

    def get_middle_selected(*args):
        sel = mc.ls(sl=True)
        if sel:
            mc.textFieldButtonGrp(middle_objs_field, edit=True, text=' '.join(sel))
        else:
            mc.warning("No objects selected!")

    mc.textFieldButtonGrp(first_obj_field, edit=True, buttonCommand=get_first_selected)
    mc.textFieldButtonGrp(last_obj_field, edit=True, buttonCommand=get_last_selected)
    mc.textFieldButtonGrp(middle_objs_field, edit=True, buttonCommand=get_middle_selected)

    # Apply button
    def apply_constraints(*args):
        first_obj = mc.textFieldButtonGrp(first_obj_field, query=True, text=True)
        last_obj = mc.textFieldButtonGrp(last_obj_field, query=True, text=True)
        middle_objs = mc.textFieldButtonGrp(middle_objs_field, query=True, text=True).split()

        if not first_obj or not last_obj or not middle_objs:
            mc.warning("Please fill all fields!")
            return

        # Compute weights based on distance along the chain
        # Use linear distance weight (closer to first_obj -> more influence from first)
        total_distance = 0
        positions = [mc.xform(obj, query=True, worldSpace=True, translation=True) for obj in [first_obj] + middle_objs + [last_obj]]

        # Compute total distance along the chain
        for i in range(len(positions) - 1):
            p1 = positions[i]; p2 = positions[i+1]
            dist = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2) ** 0.5
            total_distance += dist

        # Compute cumulative distance for each middle object
        cumulative_distance = 0
        for i, obj in enumerate(middle_objs):
            p_prev = positions[i]
            p_next = positions[i+1]
            segment_dist = ((p_next[0]-p_prev[0])**2 + (p_next[1]-p_prev[1])**2 + (p_next[2]-p_prev[2])**2) ** 0.5
            cumulative_distance += segment_dist
            w_first = max(0, 1 - (cumulative_distance / total_distance))
            w_last = 1 - w_first
            print(f"{obj}: w_first={w_first:.2f}, w_last={w_last:.2f}")

            # Apply constraints
            mc.orientConstraint(first_obj, obj, w=w_first, mo=True)
            mc.orientConstraint(last_obj, obj, w=w_last, mo=True)
            mc.pointConstraint(first_obj, obj, w=w_first, mo=True)
            mc.pointConstraint(last_obj, obj, w=w_last, mo=True)

        mc.confirmDialog(title="Done", message="Constraints applied successfully!")

    mc.button(label="Apply Uniform Twist / Point Constraints", command=apply_constraints)
    mc.showWindow(win_name)

# Run the UI
uniform_twist_ui()
