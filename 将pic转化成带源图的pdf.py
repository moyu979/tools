import os
import io
import img2pdf
import pikepdf
from PIL import Image

def create_dual_mode_manga_pdf(input_dir: str, output_pdf: str, quality: int = 95):
    """
    创建双轨 PDF：可翻页阅读 + 原始 .webp 附件 + .info 文件
    - input_dir: 目录，需包含数字命名的 .webp、.thumb 和 .info 文件
    - output_pdf: 生成的 PDF 路径
    - quality: JPEG 图像质量，默认 95（较高画质）
    """
    image_exts = ('.webp', '.jpg', '.jpeg', '.png')

    thumb_path = os.path.join(input_dir, ".thumb")
    info_path = os.path.join(input_dir, ".ehviewer")
    # if not os.path.isfile(thumb_path):
    #     raise FileNotFoundError("必须包含 .thumb")
    # if not os.path.isfile(info_path):
    #     raise FileNotFoundError("必须包含 .info")

    # 读取并排序漫画图像（数字命名）
    image_files = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith(image_exts) and f.split('.')[0].isdigit()
    ]
    if len(image_files)==0:
        return 
    image_files.sort(key=lambda f: int(os.path.splitext(f)[0]))

    # 图像路径列表：封面在最前
    image_paths = [os.path.join(input_dir, f) for f in image_files]

    # 转换图像为 JPEG（内存中）
    jpeg_bytes_list = []
    for path in image_paths:
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            bio = io.BytesIO()
            rgb.save(bio, format="JPEG", quality=quality)
            jpeg_bytes_list.append(bio.getvalue())

    # 创建临时 PDF（只有图片）
    temp_pdf = output_pdf + ".temp.pdf"
    with open(temp_pdf, "wb") as f:
        f.write(img2pdf.convert(jpeg_bytes_list))

    #加载 PDF，添加 .info 和原始 .webp 图像为附件
    with pikepdf.open(temp_pdf) as pdf:
        # 确保 /Names 字典存在
        if "/Names" not in pdf.Root:
            pdf.Root["/Names"] = pikepdf.Dictionary()
        names = pdf.Root["/Names"]
        if "/EmbeddedFiles" not in names:
            names["/EmbeddedFiles"] = pikepdf.Dictionary({"/Names": pikepdf.Array()})
        embedded_files = names["/EmbeddedFiles"]
        names_array = embedded_files["/Names"]
        all_files=image_paths.copy()
        if os.path.exists(os.path.join(in_path,".ehviewer")):
            all_files.append(".ehviewer")
        if os.path.exists(os.path.join(in_path,".thumb")):
            all_files.append(".thumb")
        for file in all_files:
            info_path=os.path.join(in_path,file)
            # 添加 .info 文件
            with open(info_path, "rb") as f:
                file_data = f.read()
                file_stream = pdf.make_stream(file_data)
                # 创建文件嵌入字典，描述这个附件
                file_spec = pikepdf.Dictionary({
                    "/Type": pikepdf.Name("/Filespec"),
                    "/F": pikepdf.String(file),   # 附件名字
                    "/EF": pikepdf.Dictionary({
                        "/F": file_stream                 # 文件流
                    }),
                    "/UF": pikepdf.String(file)   # Unicode 文件名，兼容性更好
                })
                
                # 把新附件加进去
                names_array.append(pikepdf.String(file))
                names_array.append(file_spec)
        
        pdf.save(output_pdf)

    os.remove(temp_pdf)
    print(f"✅ 成功生成双轨漫画 PDF：{output_pdf}")



if __name__=="__main__":
    path=os.path.abspath("/Volumes/未命名/download")
    files=os.listdir(path)
    for file in files:
        if file.startswith("."):
            continue
        in_path=os.path.join(path,file)
        print(in_path)
        out_path=os.path.join("./pdfs",f"{file}.pdf")
        create_dual_mode_manga_pdf(in_path,out_path)