# BlendShape transfer

If you have a character customisation for your model - this addon will help you with ajusting equipement for a character. This addon is very simple and recommendet to use with various sorts of clothing.

### What it does?
It is basically a simple loop, which goes through shapes of "targrt object", and applies this shapes for a selected object with `Mesh deformer`

### How to use?
1. Select your "targrt object" in addon window
2. Make sure, that you have BlendShapes you needed
3. Click `Apply Blendshapes` button

  And that's all!
<video src='https://github.com/user-attachments/assets/c9be5f5d-0d0c-4c25-b28d-a1283bf9f5e1' width=180/></video>

### Issues
Sometimes this addon wouldn't work, because "targrt object" has an issues. If you want to see what kind of issues it has, just play arond `Mesh deformer` and set your object as targrt in this modifier, then try to bind. You will see, what goes wrong.
Mostly it is edges with several faces attached, or n-gones
