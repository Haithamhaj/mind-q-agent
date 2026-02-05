import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Loader2, Trash2, Eye, X, FileBarChart } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Document } from '../types';
import { formatBytes } from '../lib/utils';

// Mock data
const MOCK_DOCS: Document[] = [
  { id: '1', name: 'Project_Specs.pdf', path: '/docs/1', type: 'application/pdf', size: 2500000, created_at: '2023-10-27T10:00:00Z', processed: true, progress: 100 },
  { id: '2', name: 'Meeting_Notes.txt', path: '/docs/2', type: 'text/plain', size: 12000, created_at: '2023-10-28T14:30:00Z', processed: true, progress: 100 },
  { id: '3', name: 'Q3_Financials.csv', path: '/docs/3', type: 'text/csv', size: 450000, created_at: '2023-10-29T09:15:00Z', processed: false, progress: 45 },
];

const DocumentsPage: React.FC = () => {
  const [docs, setDocs] = useState<Document[]>(MOCK_DOCS);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    
    // Prevent flickering when dragging over child elements
    if (e.currentTarget.contains(e.relatedTarget as Node)) {
      return;
    }
    setIsDragging(false);
  };

  const processFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newDocs: Document[] = Array.from(files).map((file) => ({
      id: Math.random().toString(36).substring(7),
      name: file.name,
      path: `/docs/${file.name.replace(/\s+/g, '_')}`,
      type: file.type || 'application/octet-stream',
      size: file.size,
      created_at: new Date().toISOString(),
      processed: false,
      progress: 0,
    }));

    setDocs((prev) => [...newDocs, ...prev]);

    // Simulate backend processing per file with progress
    newDocs.forEach(newDoc => {
        const duration = 2000 + Math.random() * 2000; // 2-4 seconds
        const intervalTime = 50;
        const steps = duration / intervalTime;
        let step = 0;

        const interval = setInterval(() => {
            step++;
            const progress = Math.min(Math.round((step / steps) * 100), 100);
            
            setDocs(currentDocs => currentDocs.map(doc => {
                if (doc.id === newDoc.id) {
                    if (progress === 100) {
                        return { ...doc, processed: true, progress: 100 };
                    }
                    return { ...doc, progress };
                }
                return doc;
            }));

            if (step >= steps) {
                clearInterval(interval);
            }
        }, intervalTime);
    });
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
        fileInputRef.current.value = ''; // Reset
    }
  };

  const handleSelectFilesClick = () => {
    fileInputRef.current?.click();
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDocs((prev) => prev.filter(doc => doc.id !== id));
    if (selectedDoc?.id === id) {
        setSelectedDoc(null);
    }
  };

  const handleRowClick = (doc: Document) => {
      setSelectedDoc(doc);
  };

  // Generate mock preview content
  const getPreviewContent = (doc: Document) => {
      if (doc.type === 'text/plain') {
          return (
            <div className="whitespace-pre-wrap font-mono text-sm text-zinc-700">
{`Meeting Notes - ${new Date(doc.created_at).toLocaleDateString()}

Attendees: Team Alpha
Subject: ${doc.name.replace('.txt', '')}

1. Reviewed Q3 Performance
   - User growth up by 15%
   - Server costs optimized

2. Action Items
   - [ ] Finalize API spec for Mobile App
   - [ ] Update documentation
   - [ ] Schedule team offsite

Note: This is a preview of the text file content. 
The actual file content would be fetched from the backend.`}
            </div>
          );
      }
      
      if (doc.type === 'text/csv' || doc.name.endsWith('.csv')) {
          return (
              <div className="overflow-x-auto">
                  <table className="min-w-full text-sm text-left text-zinc-600">
                      <thead className="text-xs text-zinc-700 uppercase bg-zinc-100">
                          <tr>
                              <th className="px-4 py-2">Date</th>
                              <th className="px-4 py-2">Category</th>
                              <th className="px-4 py-2">Amount</th>
                              <th className="px-4 py-2">Status</th>
                          </tr>
                      </thead>
                      <tbody>
                          <tr className="bg-white border-b">
                              <td className="px-4 py-2">2023-10-01</td>
                              <td className="px-4 py-2">Software</td>
                              <td className="px-4 py-2">$1,200</td>
                              <td className="px-4 py-2">Paid</td>
                          </tr>
                          <tr className="bg-white border-b">
                              <td className="px-4 py-2">2023-10-05</td>
                              <td className="px-4 py-2">Hosting</td>
                              <td className="px-4 py-2">$450</td>
                              <td className="px-4 py-2">Pending</td>
                          </tr>
                          <tr className="bg-white border-b">
                              <td className="px-4 py-2">2023-10-12</td>
                              <td className="px-4 py-2">Services</td>
                              <td className="px-4 py-2">$3,000</td>
                              <td className="px-4 py-2">Paid</td>
                          </tr>
                      </tbody>
                  </table>
                  <p className="mt-4 text-xs text-zinc-400 italic">Showing first 3 rows of {doc.name}</p>
              </div>
          );
      }

      return (
          <div className="flex flex-col items-center justify-center h-48 text-zinc-400">
              <FileBarChart className="w-12 h-12 mb-3 opacity-20" />
              <p>Preview not available for this file type.</p>
              <p className="text-xs mt-1">({doc.type})</p>
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
        <Button onClick={handleSelectFilesClick}>
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
        </Button>
      </div>

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
        className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all duration-200 ease-in-out mb-8 ${
          isDragging 
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
        <p className="text-zinc-500 mt-1 mb-4 text-sm">PDF, DOCX, TXT, CSV supported (Max 50MB)</p>
        <Button 
            variant={isDragging ? "primary" : "secondary"} 
            size="sm" 
            onClick={(e) => {
                e.stopPropagation();
                handleSelectFilesClick();
            }}
        >
            Select Files
        </Button>
      </div>

      {/* Documents Table */}
      <div className="bg-white border border-zinc-200 rounded-lg shadow-sm overflow-hidden">
        {docs.length === 0 ? (
             <div className="p-8 text-center text-zinc-500">
                No documents uploaded yet.
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
                            {new Date(doc.created_at).toLocaleDateString()}
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
                      <Button onClick={() => alert('Download functionality would happen here')}>Download</Button>
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