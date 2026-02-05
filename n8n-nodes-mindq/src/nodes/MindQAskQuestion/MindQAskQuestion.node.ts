import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQAskQuestion implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Ask Question',
        name: 'mindQAskQuestion',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        description: 'Ask questions using Mind-Q knowledge',
        defaults: {
            name: 'Mind-Q Ask Question',
        },
        inputs: ['main'],
        outputs: ['main'],
        credentials: [
            {
                name: 'mindQApi',
                required: true,
            },
        ],
        properties: [
            {
                displayName: 'Question',
                name: 'question',
                type: 'string',
                typeOptions: {
                    rows: 2,
                },
                default: '',
                placeholder: 'Ask a question',
                description: 'Question to ask',
            },
            {
                displayName: 'Use Context',
                name: 'useContext',
                type: 'boolean',
                default: true,
                description: 'Whether to use Mind-Q knowledge for context',
            },
        ],
    };

    async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
        const items = this.getInputData();
        const returnData: INodeExecutionData[] = [];

        const credentials = await this.getCredentials('mindQApi');
        const apiUrl = credentials.apiUrl as string;
        const apiKey = credentials.apiKey as string;

        for (let i = 0; i < items.length; i++) {
            const question = this.getNodeParameter('question', i) as string;
            const useContext = this.getNodeParameter('useContext', i) as boolean;

            const response = await axios.post(
                `${apiUrl}/chat/ask`,
                {
                    question,
                    use_context: useContext,
                },
                {
                    headers: {
                        'X-API-Key': apiKey,
                        'Content-Type': 'application/json',
                    },
                }
            );

            returnData.push({
                json: response.data,
                pairedItem: { item: i },
            });
        }

        return [returnData];
    }
}
