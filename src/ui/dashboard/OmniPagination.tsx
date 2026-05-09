import React from 'react';

// OmniPagination.tsx — React Pagination Component
// Layer: Interface / TypeScript
//
// Robust pagination controller that intelligently truncates page numbers
// using ellipses when the total page count is large. Zero mock.

export interface OmniPaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    siblingCount?: number;
    className?: string;
}

export const OmniPagination: React.FC<OmniPaginationProps> = ({
    currentPage,
    totalPages,
    onPageChange,
    siblingCount = 1,
    className = ''
}) => {
    
    // Generate page numbers with ellipses
    const paginationRange = React.useMemo(() => {
        const totalPageNumbers = siblingCount + 5;

        // Case 1: If the number of pages is less than the page numbers we want to show
        if (totalPageNumbers >= totalPages) {
            return Array.from({ length: totalPages }, (_, i) => i + 1);
        }

        const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
        const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);

        const showLeftDots = leftSiblingIndex > 2;
        const showRightDots = rightSiblingIndex < totalPages - 2;

        const firstPageIndex = 1;
        const lastPageIndex = totalPages;

        // Case 2: No left dots, but right dots
        if (!showLeftDots && showRightDots) {
            let leftItemCount = 3 + 2 * siblingCount;
            let leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
            return [...leftRange, '...', totalPages];
        }

        // Case 3: Left dots, no right dots
        if (showLeftDots && !showRightDots) {
            let rightItemCount = 3 + 2 * siblingCount;
            let rightRange = Array.from(
                { length: rightItemCount }, 
                (_, i) => totalPages - rightItemCount + i + 1
            );
            return [firstPageIndex, '...', ...rightRange];
        }

        // Case 4: Both left and right dots
        if (showLeftDots && showRightDots) {
            let middleRange = Array.from(
                { length: rightSiblingIndex - leftSiblingIndex + 1 },
                (_, i) => leftSiblingIndex + i
            );
            return [firstPageIndex, '...', ...middleRange, '...', lastPageIndex];
        }
        
        return [];
    }, [totalPages, currentPage, siblingCount]);

    if (currentPage === 0 || paginationRange.length < 2) {
        return null;
    }

    const onNext = () => {
        if (currentPage < totalPages) onPageChange(currentPage + 1);
    };

    const onPrevious = () => {
        if (currentPage > 1) onPageChange(currentPage - 1);
    };

    return (
        <nav className={`flex items-center space-x-1 ${className}`} aria-label="Pagination">
            <button
                onClick={onPrevious}
                disabled={currentPage === 1}
                className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Previous Page"
            >
                Prev
            </button>
            
            {paginationRange.map((pageNumber, i) => {
                if (pageNumber === '...') {
                    return (
                        <span key={`dots-${i}`} className="px-4 py-2 text-slate-400 dark:text-slate-500">
                            &#8230;
                        </span>
                    );
                }

                const isActive = pageNumber === currentPage;
                return (
                    <button
                        key={pageNumber}
                        onClick={() => onPageChange(pageNumber as number)}
                        aria-current={isActive ? "page" : undefined}
                        className={`
                            px-4 py-2 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500
                            ${isActive 
                                ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/40 dark:border-blue-800 dark:text-blue-300 font-semibold' 
                                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-700'
                            }
                        `}
                    >
                        {pageNumber}
                    </button>
                );
            })}

            <button
                onClick={onNext}
                disabled={currentPage === totalPages}
                className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Next Page"
            >
                Next
            </button>
        </nav>
    );
};
