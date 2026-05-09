// moe_chat_navigator_sidebar.ts — Interface Layer: Chat Navigator Sidebar
// Pure DOM TypeScript injecting a navigation sidebar into Web Chat applications.

export class ChatSidebar {
    private container: HTMLElement;

    constructor() {
        this.container = document.createElement('div');
        this.container.id = 'omni-chat-navigator';
        this.container.style.position = 'fixed';
        this.container.style.right = '0';
        this.container.style.top = '0';
        this.container.style.width = '250px';
        this.container.style.height = '100vh';
        this.container.style.backgroundColor = '#1e1e1e';
        this.container.style.color = '#fff';
        this.container.style.padding = '15px';
        this.container.style.boxShadow = '-2px 0 5px rgba(0,0,0,0.5)';
        this.container.style.overflowY = 'auto';
        this.container.style.zIndex = '9999';
        
        document.body.appendChild(this.container);
        this.renderHeader();
    }

    private renderHeader() {
        const title = document.createElement('h3');
        title.innerText = 'Conversation Outline';
        title.style.margin = '0 0 15px 0';
        title.style.borderBottom = '1px solid #444';
        title.style.paddingBottom = '10px';
        this.container.appendChild(title);
    }

    public addOutlineItem(text: string, elementId: string) {
        const item = document.createElement('a');
        item.innerText = text;
        item.href = `#${elementId}`;
        item.style.display = 'block';
        item.style.color = '#ccc';
        item.style.textDecoration = 'none';
        item.style.marginBottom = '8px';
        item.style.fontSize = '14px';
        
        item.onmouseover = () => item.style.color = '#fff';
        item.onmouseout = () => item.style.color = '#ccc';
        
        this.container.appendChild(item);
    }
}
