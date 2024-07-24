import requests
import gradio as gr

def get_response(prompt):
    response = requests.post(backend_url, json={"prompt": prompt})

    if response.status_code != 200:
        return "Error: " + str(response.status_code)

    return response.json()["response"]


def add_text(history, text):
    history = history + [(text, None)]
    return history, text


def bot(history, text):
    response = get_response(text)
    history[-1][1] = response
    return history, ""


backend_url = "http://localhost:7000"


def main():
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot([], elem_id="chatbot", height=800)

        with gr.Row():
            with gr.Column(scale=0.85):
                txt = gr.Textbox(
                    show_label=False,
                    placeholder="Enter text and press enter",
                    container=False,
                )
            with gr.Column(scale=0.15, min_width=0):
                reset = gr.Button("Reset")

        txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
            bot, [chatbot, txt], [chatbot, txt]
        )
        reset.click(lambda: None, None, chatbot, queue=False)

    demo.launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
