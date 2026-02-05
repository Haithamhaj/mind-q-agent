import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQAddDocument implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Add Document',
        name: 'mindQAddDocument',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        description: 'Add document to Mind-Q',
        defaults: {
            name: 'Mind-Q Add Document',
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
                displayName: 'Title',
                name: 'title',
                type: 'string',
                default: '',
                placeholder: 'Document title',
                description: 'Title of the document',
            },
            {
                displayName: 'Content',
                name: 'content',
                type: 'string',
                typeOptions: {
                    rows: 4,
                },
                default: '',
                placeholder: 'Document content',
                description: 'Content of the document',
            },
            {
                displayName: 'Source',
                name: 'source',
                type: 'string',
                default: 'n8n_automation',
                description: 'Source identifier',
            },
            {
                displayName: 'Tags',
                name: 'tags',
                type: 'string',
                default: '',
                placeholder: 'tag1, tag2, tag3',
                description: 'Comma-separated tags',
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
            const title = this.getNodeParameter('title', i) as string;
            const content = this.getNodeParameter('content', i) as string;
            const source = this.getNodeParameter('source', i) as string;
            const tagsString = this.getNodeParameter('tags', i) as string;

            const tags = tagsString ? tagsString.split(',').map(t => t.trim()) : [];

            const response = await axios.post(
                `${apiUrl}/documents`,
                {
                    title,
                    content,
                    source,
                    tags,
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
