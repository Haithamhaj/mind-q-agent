import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Upload, FileText, CheckCircle, Loader2, Trash2, Eye, X, FileBarChart, RefreshCw, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Document } from '../api/types';
import { formatBytes } from '../lib/utils';

const API_BASE = '/api/v1';

// Backend document response type
interface BackendDocument {
    hash: string;
    title: string;
    created_at: string;
    size: number;
}

// Convert backend format to frontend format
const mapBackendToFrontend = (doc: BackendDocument): Document => ({
    id: doc.hash,
    name: doc.title || 'Untitled',
    path: `/docs/${doc.hash}`,
    type: doc.title?.split('.').pop() || 'unknown',
    size: doc.size || 0,
    created_at: doc.created_at,
    processed: true,
    progress: 100,
});

const DocumentsPage: React.FC = () => {
    const [docs, setDocs] = useState<Document[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Fetch documents from API
    const fetchDocuments = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/documents/`);
            if (!response.ok) {
                throw new Error(`Failed to fetch documents: ${response.statusText}`);
            }
            const data: BackendDocument[] = await response.json();
            setDocs(data.map(mapBackendToFrontend));
        } catch (err) {
            console.error('Fetch documents error:', err);
            setError(err instanceof Error ? err.message : 'Failed to load documents');
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load documents on mount
    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        if (e.currentTarget.contains(e.relatedTarget as Node)) {
            return;
        }
        setIsDragging(false);
    };

    // Upload file to backend
    const uploadFile = async (file: File): Promise<boolean> => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE}/documents/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
            }

            return true;
        } catch (err) {
            console.error('Upload error:', err);
            throw err;
        }
    };

    const processFiles = async (files: FileList | null) => {
        if (!files || files.length === 0) return;

        setIsUploading(true);
        setError(null);

        // Create temporary entries with progress
        const tempDocs: Document[] = Array.from(files).map((file) => ({
            id: `temp-${Math.random().toString(36).substring(7)}`,
            name: file.name,
            path: `/docs/${file.name.replace(/\s+/g, '_')}`,
            type: file.type || 'application/octet-stream',
            size: file.size,
            created_at: new Date().toISOString(),
            processed: false,
            progress: 0,
        }));

        setDocs((prev) => [...tempDocs, ...prev]);

        // Upload each file
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const tempDoc = tempDocs[i];

            // Animate progress
            const progressInterval = setInterval(() => {
                setDocs(currentDocs => currentDocs.map(doc => {
                    if (doc.id === tempDoc.id && doc.progress !== undefined && doc.progress < 90) {
                        return { ...doc, progress: doc.progress + 10 };
                    }
                    return doc;
                }));
            }, 200);

            try {
                await uploadFile(file);

                clearInterval(progressInterval);

                // Mark as complete
                setDocs(currentDocs => currentDocs.map(doc => {
                    if (doc.id === tempDoc.id) {
                        return { ...doc, processed: true, progress: 100 };
                    }
                    return doc;
                }));
            } catch (err) {
                clearInterval(progressInterval);

                // Remove failed upload from list
                setDocs(currentDocs => currentDocs.filter(doc => doc.id !== tempDoc.id));
                setError(`Failed to upload ${file.name}: ${err instanceof Error ? err.message : 'Unknown error'}`);
            }
        }

        setIsUploading(false);
        // Refresh the list to get accurate data from backend
        await fetchDocuments();
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const { files } = e.dataTransfer;
        processFiles(files);
    };

    const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        processFiles(e.target.files);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleSelectFilesClick = () => {
        fileInputRef.current?.click();
    };

    const handleDelete = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        // Note: Delete API not implemented in backend yet
        // For now, just remove from local state with a warning
        if (confirm('Delete functionality is not yet implemented in the backend. Remove from view only?')) {
            setDocs((prev) => prev.filter(doc => doc.id !== id));
            if (selectedDoc?.id === id) {
                setSelectedDoc(null);
            }
        }
    };

    const handleRowClick = (doc: Document) => {
        setSelectedDoc(doc);
    };

    const getPreviewContent = (doc: Document) => {
        if (doc.type === 'text/plain' || doc.name.endsWith('.txt')) {
            return (
                <div className="whitespace-pre-wrap font-mono text-sm text-zinc-700">
                    <p className="text-zinc-500 italic">Text preview not available. Document has been processed and indexed.</p>
                </div>
            );
        }

        if (doc.type === 'text/csv' || doc.name.endsWith('.csv')) {
            return (
                <div className="flex flex-col items-center justify-center h-48 text-zinc-400">
                    <FileBarChart className="w-12 h-12 mb-3 opacity-20" />
                    <p>CSV file processed and indexed.</p>
                </div>
            );
        }

        return (
            <div className="flex flex-col items-center justify-center h-48 text-zinc-400">
                <FileBarChart className="w-12 h-12 mb-3 opacity-20" />
                <p>Document has been processed and indexed.</p>
                <p className="text-xs mt-1">({doc.type || 'Unknown type'})</p>
            </div>
        );
    };

    return (
        <div className="p-8 max-w-6xl mx-auto relative">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900">Knowledge Library</h1>
                    <p className="text-zinc-500 mt-1">Manage documents for context and retrieval.</p>
                </div>
                <div className="flex gap-2">
                    <Button onClick={fetchDocuments} variant="secondary" disabled={isLoading}>
                        <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button onClick={handleSelectFilesClick} disabled={isUploading}>
                        <Upload className="w-4 h-4 mr-2" />
                        {isUploading ? 'Uploading...' : 'Upload Document'}
                    </Button>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span>{error}</span>
                    <button onClick={() => setError(null)} className="ml-auto p-1 hover:bg-red-100 rounded">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}

            {/* Hidden File Input */}
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileInputChange}
                className="hidden"
                multiple
            />

            {/* Drag & Drop Zone */}
            <div
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all duration-200 ease-in-out mb-8 ${isDragging
                    ? 'border-blue-500 bg-blue-50 scale-[1.01]'
                    : 'border-zinc-300 hover:border-zinc-400 bg-zinc-50'
                    }`}
            >
                <div className={`w-12 h-12 rounded-full shadow-sm flex items-center justify-center mb-4 transition-colors ${isDragging ? 'bg-blue-200' : 'bg-white'}`}>
                    <Upload className={`w-6 h-6 ${isDragging ? 'text-blue-700' : 'text-blue-600'}`} />
                </div>
                <h3 className="text-lg font-medium text-zinc-900">
                    {isDragging ? 'Drop files to upload' : 'Drop files here to upload'}
                </h3>
                <p className="text-zinc-500 mt-1 mb-4 text-sm">PDF, DOCX, TXT, CSV, MD supported (Max 50MB)</p>
                <Button
                    variant={isDragging ? "primary" : "secondary"}
                    size="sm"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleSelectFilesClick();
                    }}
                    disabled={isUploading}
                >
                    {isUploading ? 'Uploading...' : 'Select Files'}
                </Button>
            </div>

            {/* Documents Table */}
            <div className="bg-white border border-zinc-200 rounded-lg shadow-sm overflow-hidden">
                {isLoading ? (
                    <div className="p-8 text-center">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-3" />
                        <p className="text-zinc-500">Loading documents...</p>
                    </div>
                ) : docs.length === 0 ? (
                    <div className="p-8 text-center text-zinc-500">
                        No documents uploaded yet. Drop files above to get started.
                    </div>
                ) : (
                    <table className="w-full text-left text-sm">
                        <thead className="bg-zinc-50 border-b border-zinc-200 text-zinc-500">
                            <tr>
                                <th className="px-6 py-3 font-medium">Name</th>
                                <th className="px-6 py-3 font-medium w-48">Status</th>
                                <th className="px-6 py-3 font-medium">Size</th>
                                <th className="px-6 py-3 font-medium">Uploaded</th>
                                <th className="px-6 py-3 font-medium text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-100">
                            {docs.map((doc) => (
                                <tr
                                    key={doc.id}
                                    onClick={() => handleRowClick(doc)}
                                    className="hover:bg-zinc-50/80 transition-colors cursor-pointer group"
                                >
                                    <td className="px-6 py-4">
                                        <div className="flex items-center">
                                            <div className="w-8 h-8 rounded bg-blue-50 flex items-center justify-center mr-3 text-blue-600">
                                                <FileText className="w-4 h-4" />
                                            </div>
                                            <span className="font-medium text-zinc-900 truncate max-w-[200px] group-hover:text-blue-600 transition-colors">
                                                {doc.name}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        {doc.processed ? (
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                <CheckCircle className="w-3 h-3 mr-1" /> Ready
                                            </span>
                                        ) : (
                                            <div className="w-full max-w-[140px]">
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className="inline-flex items-center text-xs font-medium text-amber-600">
                                                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                                        Processing
                                                    </span>
                                                    <span className="text-xs font-mono text-zinc-500">{doc.progress || 0}%</span>
                                                </div>
                                                <div className="w-full bg-zinc-100 rounded-full h-1.5 overflow-hidden">
                                                    <div
                                                        className="bg-amber-500 h-full rounded-full transition-all duration-200"
                                                        style={{ width: `${doc.progress || 0}%` }}
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-zinc-500 font-mono text-xs">{formatBytes(doc.size)}</td>
                                    <td className="px-6 py-4 text-zinc-500">
                                        {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'Unknown'}
                                    </td>
                                    <td className="px-6 py-4 text-right flex justify-end gap-2">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="text-zinc-400 hover:text-blue-600"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleRowClick(doc);
                                            }}
                                        >
                                            <Eye className="w-4 h-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="text-zinc-400 hover:text-red-600"
                                            onClick={(e) => handleDelete(doc.id, e)}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Preview Modal */}
            {selectedDoc && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/40 backdrop-blur-sm animate-in fade-in duration-200">
                    <div
                        className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Modal Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100 bg-white">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                                    <FileText className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-zinc-900 leading-none">{selectedDoc.name}</h3>
                                    <p className="text-xs text-zinc-500 mt-1.5">{formatBytes(selectedDoc.size)} • {selectedDoc.type}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedDoc(null)}
                                className="p-2 rounded-full hover:bg-zinc-100 text-zinc-400 hover:text-zinc-600 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Modal Content */}
                        <div className="flex-1 overflow-auto p-6 bg-zinc-50">
                            <div className="bg-white rounded-lg border border-zinc-200 shadow-sm p-6 min-h-[200px]">
                                {getPreviewContent(selectedDoc)}
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="px-6 py-4 border-t border-zinc-100 bg-white flex justify-end gap-3">
                            <Button variant="secondary" onClick={() => setSelectedDoc(null)}>Close</Button>
                        </div>
                    </div>
                    {/* Click outside to close */}
                    <div className="absolute inset-0 -z-10" onClick={() => setSelectedDoc(null)} />
                </div>
            )}
        </div>
    );
};

export default DocumentsPage;