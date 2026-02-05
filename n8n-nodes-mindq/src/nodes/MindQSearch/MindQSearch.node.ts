import {
    IExecuteFunctions,
    INodeExecutionData,
    INodeType,
    INodeTypeDescription,
    NodeOperationError,
} from 'n8n-workflow';

import axios from 'axios';

export class MindQSearch implements INodeType {
    description: INodeTypeDescription = {
        displayName: 'Mind-Q Search',
        name: 'mindQSearch',
        icon: 'file:mindq.svg',
        group: ['transform'],
        version: 1,
        subtitle: '={{$parameter["operation"]}}',
        description: 'Search Mind-Q Knowledge Graph',
        defaults: {
            name: 'Mind-Q Search',
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
                        name: 'Search',
                        value: 'search',
                        description: 'Search for content',
                        action: 'Search for content',
                    },
                    {
                        name: 'Get Recent',
                        value: 'recent',
                        description: 'Get recent documents',
                        action: 'Get recent documents',
                    },
                ],
                default: 'search',
            },
            {
                displayName: 'Query',
                name: 'query',
                type: 'string',
                displayOptions: {
                    show: {
                        operation: ['search'],
                    },
                },
                default: '',
                placeholder: 'Enter search query',
                description: 'What to search for in Mind-Q',
            },
            {
                displayName: 'Search Type',
                name: 'searchType',
                type: 'options',
                displayOptions: {
                    show: {
                        operation: ['search'],
                    },
                },
                options: [
                    {
                        name: 'Semantic',
                        value: 'semantic',
                    },
                    {
                        name: 'Keyword',
                        value: 'keyword',
                    },
                    {
                        name: 'Concept',
                        value: 'concept',
                    },
                ],
                default: 'semantic',
            },
            {
                displayName: 'Max Results',
                name: 'maxResults',
                type: 'number',
                default: 10,
                description: 'Maximum number of results to return',
            },
            {
                displayName: 'Time Range (hours)',
                name: 'timeRange',
                type: 'number',
                displayOptions: {
                    show: {
                        operation: ['recent'],
                    },
                },
                default: 24,
                description: 'Get documents from last N hours',
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
            try {
                const operation = this.getNodeParameter('operation', i) as string;

                let results;

                if (operation === 'search') {
                    const query = this.getNodeParameter('query', i) as string;
                    const searchType = this.getNodeParameter('searchType', i) as string;
                    const maxResults = this.getNodeParameter('maxResults', i) as number;

                    const response = await axios.post(
                        `${apiUrl}/search`,
                        {
                            query,
                            search_type: searchType,
                            max_results: maxResults,
                        },
                        {
                            headers: {
                                'X-API-Key': apiKey,
                                'Content-Type': 'application/json',
                            },
                        }
                    );

                    results = response.data;
                } else if (operation === 'recent') {
                    const timeRange = this.getNodeParameter('timeRange', i) as number;
                    const maxResults = this.getNodeParameter('maxResults', i) as number;

                    const response = await axios.get(
                        `${apiUrl}/documents/recent`,
                        {
                            params: {
                                hours: timeRange,
                                limit: maxResults,
                            },
                            headers: {
                                'X-API-Key': apiKey,
                            },
                        }
                    );

                    results = response.data;
                }

                returnData.push({
                    json: results,
                    pairedItem: { item: i },
                });
            } catch (error: any) {
                if (this.continueOnFail()) {
                    returnData.push({
                        json: {
                            error: error.message,
                        },
                        pairedItem: { item: i },
                    });
                    continue;
                }
                throw new NodeOperationError(this.getNode(), error);
            }
        }

        return [returnData];
    }
}
