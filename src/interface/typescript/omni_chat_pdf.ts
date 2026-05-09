import { PDFLoader } from "langchain/document_loaders/fs/pdf";
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { ChatOpenAI } from "@langchain/openai";
import { ConversationalRetrievalQAChain } from "langchain/chains";
import * as fs from "fs";

export class OmniChatPDF {
    private vectorStore: MemoryVectorStore | null = null;
    private chain: ConversationalRetrievalQAChain | null = null;

    constructor(private openAIApiKey: string) {
        if (!openAIApiKey) {
            throw new Error("OMNI ChatPDF: OpenAI API Key is required.");
        }
    }

    /**
     * Ingests a PDF file, parses it, creates embeddings and stores them in memory.
     */
    async ingestPDF(filePath: string): Promise<void> {
        if (!fs.existsSync(filePath)) {
            throw new Error(`File not found: ${filePath}`);
        }
        
        const loader = new PDFLoader(filePath, { splitPages: true });
        const docs = await loader.load();
        
        this.vectorStore = await MemoryVectorStore.fromDocuments(
            docs,
            new OpenAIEmbeddings({ openAIApiKey: this.openAIApiKey })
        );

        const model = new ChatOpenAI({ 
            openAIApiKey: this.openAIApiKey, 
            modelName: "gpt-4-turbo-preview",
            temperature: 0.2
        });

        this.chain = ConversationalRetrievalQAChain.fromLLM(
            model,
            this.vectorStore.asRetriever(3) // retrieve top 3 relevant chunks
        );
    }

    /**
     * Query the ingested PDF using conversational retrieval.
     */
    async query(question: string, chatHistory: [string, string][] = []): Promise<string> {
        if (!this.chain) {
            throw new Error("OMNI ChatPDF: Vector store uninitialized. Call ingestPDF first.");
        }
        const res = await this.chain.call({ 
            question, 
            chat_history: chatHistory.map(h => `${h[0]}\n${h[1]}`).join("\n")
        });
        return res.text;
    }
}
