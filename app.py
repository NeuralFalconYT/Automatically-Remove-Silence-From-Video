import os
import subprocess


def get_video_duration(video_path):
    """Return video duration as (hours, minutes, seconds)"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of",
             "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(result.stdout.strip())
        
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        return hours, minutes, seconds
    except Exception as e:
        print("Error:", e)
        return None


def edit(video_path, keep_silence_up_to=0.2,high_quality=False,save_folder="./Remove-Silence/"):
    os.makedirs(save_folder, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    save_path = os.path.join(save_folder, f"{base_name}_ALTERED.mp4")

    cmd = [
        "auto-editor",
        os.path.abspath(video_path),
        "--margin", f"{keep_silence_up_to}sec",
        "--no-open",
        "--temp-dir", "./temp/",
        "-o", save_path
    ]

    if high_quality:
        cmd.extend([
            "-c:v", "libx264",
            "-b:v", "12M",
            "-profile:v", "high",
            "-c:a", "aac",
            "-b:a", "192k"
        ])

    try:
        print("Running command:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        save_path = os.path.abspath(save_path)

        # get durations
        input_duration = get_video_duration(os.path.abspath(video_path))
        output_duration = get_video_duration(save_path)

        # prepare logs
        logs = f"""original Video Duration:  {input_duration[0]} Hour {input_duration[1]} Minute {input_duration[2]} Second
After Removing Silences:  {output_duration[0]} Hour {output_duration[1]} Minute {output_duration[2]} Second"""

        return save_path, logs
    except Exception as e:
        print("Error:", e)
        return None, None

import gradio as gr

def ui():
    with gr.Blocks(title="Automatically Remove Silence From Video") as demo:
        gr.Markdown("## 🎬 Automatically Remove Silence From Video")
        gr.Markdown("Upload an .mp4 video, and silent parts will be removed automatically.")

        with gr.Row():
            with gr.Column():
                video_input = gr.File(label="Upload Video")
                run_btn = gr.Button("Process Video")
                with gr.Accordion('🎥 Video Settings', open=False):
                    silence_value = gr.Number(label="Keep Silence Upto (In seconds)", value=0.2)
                    high_quality = gr.Checkbox(value=False, label='Export in High Quality')
            with gr.Column():
                output_file = gr.File(label="Download Video File")
                duration_info = gr.Textbox(label="Duration", interactive=False)

        # hook function to button
        run_btn.click(
            fn=edit,
            inputs=[video_input, silence_value,high_quality],
            outputs=[output_file, duration_info]
        )

    return demo


# demo = ui()
# demo.queue().launch(debug=True, share=True)


import click
@click.command()
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode.")
@click.option("--share", is_flag=True, default=False, help="Enable sharing of the interface.")
def main(debug, share):
    demo=ui()
    demo.queue().launch(debug=debug, share=share)
if __name__ == "__main__":
    main()    
