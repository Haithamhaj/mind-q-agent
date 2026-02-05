import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQGetConcepts implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Get Concepts',
        name: 'mindQGetConcepts',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        description: 'Extract concepts from Mind-Q',
        defaults: {
            name: 'Mind-Q Get Concepts',
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
                displayName: 'Operation',
                name: 'operation',
                type: 'options',
                noDataExpression: true,
                options: [
                    {
                        name: 'Top Concepts',
                        value: 'top',
                        description: 'Get top weighted concepts',
                    },
                    {
                        name: 'Related Concepts',
                        value: 'related',
                        description: 'Get concepts related to a given concept',
                    },
                ],
                default: 'top',
            },
            {
                displayName: 'Concept Name',
                name: 'conceptName',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: ['related'],
                    },
                },
                default: '',
                placeholder: 'Enter concept name',
            },
            {
                displayName: 'Limit',
                name: 'limit',
                type: 'number',
                default: 10,
                description: 'Number of concepts to return',
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
            const operation = this.getNodeParameter('operation', i) as string;
            const limit = this.getNodeParameter('limit', i) as number;

            let endpoint = '';
            let params: any = { limit };

            if (operation === 'top') {
                endpoint = '/graph/concepts/top';
            } else if (operation === 'related') {
                const conceptName = this.getNodeParameter('conceptName', i) as string;
                endpoint = `/graph/concepts/${conceptName}/related`;
            }

            const response = await axios.get(`${apiUrl}${endpoint}`, {
                params,
                headers: {
                    'X-API-Key': apiKey,
                },
            });

            returnData.push({
                json: response.data,
                pairedItem: { item: i },
            });
        }

        return [returnData];
    }
}
