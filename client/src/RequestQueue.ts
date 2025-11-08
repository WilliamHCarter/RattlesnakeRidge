/**
 * RequestQueue manages a queue of asynchronous requests to ensure
 * only one request is processed at a time, preventing race conditions
 * and "generator already executing" errors on the backend.
 */
export class RequestQueue {
  private queue: Array<() => Promise<any>> = [];
  private processing: boolean = false;

  /**
   * Add a request to the queue and return a promise that resolves
   * when the request completes.
   */
  async enqueue<T>(requestFn: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await requestFn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });

      // Start processing if not already processing
      if (!this.processing) {
        this.processNext();
      }
    });
  }

  /**
   * Process the next request in the queue.
   */
  private async processNext(): Promise<void> {
    if (this.queue.length === 0) {
      this.processing = false;
      return;
    }

    this.processing = true;
    const nextRequest = this.queue.shift();

    if (nextRequest) {
      try {
        await nextRequest();
      } catch (error) {
        console.error("Request queue error:", error);
      }

      // Process the next request in the queue
      this.processNext();
    }
  }

  /**
   * Check if the queue is currently processing a request.
   */
  get isProcessing(): boolean {
    return this.processing;
  }

  /**
   * Get the number of pending requests in the queue.
   */
  get size(): number {
    return this.queue.length;
  }
}
