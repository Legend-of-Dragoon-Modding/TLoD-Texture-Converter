***
# **TLoD-Texture-Converter**
***
---
The idea behind this tool is to export/preview/preserve Textures as originally shown ingame, so BE AWARE if you see some textures translucent, is not an error, actually are the options which developers used to configure the Texture Data.

## BETA 0.2

You check the releases and you will find a Windows Version of it (Tested in Windows 10)
if not, you can compile it yourself (Sorry Linux/MAC Users i'm not so skilled to port into it).

Tested the full batch conversion on:
Processor: i5-15400F CPU at 4,4GHz.
RAM: 32 GB.
SSD: NV2 PCIe 4.0 NVMe.

Total Space required approximately: 150MB.
Time to convert all the files: 02 Minutes 07 Seconds.

Keep in mind, surely this tool can be executed in lower PC specifications, but the time to
convert the Textures will depend on how fast your Hardware is.


A simple converter to PNG (Portable Network Graphics) format oriented to work with TLoD Texture formats. Python coded (recommended Python version 3.12.0 64bit).

First of all you'll need to download Severed Chains, install it and run the game from it,
once you get the files dump, you can continue using TLoD Texture Converter.

In the first run, the tool will ask the SC/files/... path:

>files/ path: Path to files folder (which is the dump done by SC).

Then will ask you the folder you want to dump the converted files:

>C:\your_modding_folder\TLoD_Textures\


**UPDATE: TOOL COMES WITH A DOCUMENT ABOUT HOW TO USE IT**

**----"ADVANCED CONVERSION" SUPPORT----**
Texture Type supported: **PXL**

This file format is used mostly for SubMap model texturing (like Mini Dart walking model),
at the moment i didn't add TIM or MCQ. MCQ not needed because the only files are already listed and ready to be converted and TIM, because i plan to add a full SubMap Mapping, so will be listed on the future.

Format Knowledge:
TIM: Standard PS1 Texture/Image File Format.
MCQ: 3D Model Environment Skybox Texture/Image, used mostly for the Skyboxes present in game, but also in the "changing CD" stances.
PXL: Texture/Image format used usually for 3D Objects present in SubMaps, Dart Walking Model, Treasure Chest and others.

Recommend to use the File Mapping document, to know where non listed textures files are located.

---

SC done by Monoxide:

## **Severed Chains by Monoxide**

*[Severed-Chains](https://github.com/Legend-of-Dragoon-Modding/Legend-of-Dragoon-Java)*


**_File Mapping Document_**

*[File Mapping Doc](https://docs.google.com/spreadsheets/d/1wso1zNTpeQM2WmxW73-hVLs4bKdGa_6jswWuKdFtavE/edit?usp=share_link)*

---

**TLOD Texure Converter - By DooMMetaL (AKA - DragoonSouls):**

THANKS to BETA-TESTERS:

DrewUniverse and Guilty!, they took their precious time to check if this tool is working as intended!, a VERY BIG THANKS!.

i want to thanks a lot to this people who came my main inspiration to learn programming!:

TheFlyingZamboni Monoxide Zychronix

Also a special thanks to Monoxide, who did an impressive job reversing TLoD Game Engine!.

Also a special thanks to theflyingzamboni, who did an impressive job reversing Texture formats from the game, this allow me to easily write some code over it using his snippets!.

and all the people from the TLoD Global Discord!. Cheers!.


### **DISCORD**

You can find me here:

**[Discord](https://discord.gg/legendofdragoon)**

### **CHANGELOG**

```
BETA 0.1 version
ADDING SUPPORT FOR THE NEW TEXTURE PLACEMENT
BIG IMPROVES OVER CONVERSION TIME
FIXING SOME REDUNDANT AND NONSENSE CODE

BETA 0.1 version
FIRST RELEASE
Initial Comment and a little explain about this tool
```


![GUI](https://raw.githubusercontent.com/dragoonsouls/TLoD-Texture-Converter/main/Preview_Images/Main_preview.png)
![GUI1](https://raw.githubusercontent.com/dragoonsouls/TLoD-Texture-Converter/main/Preview_Images/Preview_Converter.png)
![GUI2](https://raw.githubusercontent.com/dragoonsouls/TLoD-Texture-Converter/main/Preview_Images/Preview_1.png)
![GUI3](https://raw.githubusercontent.com/dragoonsouls/TLoD-Texture-Converter/main/Preview_Images/Preview_2.png)
![GUI4](https://raw.githubusercontent.com/dragoonsouls/TLoD-Texture-Converter/main/Preview_Images/Preview_3.png)
![GUI5](https://raw.githubusercontent.com/dragoonsouls/TLoD-Texture-Converter/main/Preview_Images/Preview_4.png)


