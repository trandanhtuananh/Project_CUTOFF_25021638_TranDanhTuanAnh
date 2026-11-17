import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Locale;
import java.util.Random;

public class CutoffExperiment {

    private static final int SEED = 42;
    private static final int TRIALS = 20;
    private static final int MIN_CUTOFF = 1;
    private static final int MAX_CUTOFF = 32;
    private static final int WARMUP_RUNS = 5;

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        System.out.println("===============================================================================");
        System.out.println("   MERGESORT OPTIMAL CUTOFF BENCHMARK EXPERIMENT");
        System.out.println("   Platform : Java " + System.getProperty("java.version") + " (" + System.getProperty("os.name") + ")");
        System.out.println("   Config   : Seed=" + SEED + ", Trials=" + TRIALS + ", Cutoff range=[" + MIN_CUTOFF + ".." + MAX_CUTOFF + "]");
        System.out.println("===============================================================================\n");

        // Warm-up JVM thoroughly to trigger C1/C2 JIT compilation for all branches
        runWarmup();

        int[] sizes = {500_000, 1_000_000};
        String csvFileName = "experiment_results.csv";

        try (PrintWriter writer = new PrintWriter(new FileWriter(csvFileName))) {
            // Write CSV header
            writer.println("N,Cutoff,Mean_Time_ms,StdDev_ms,Min_Time_ms,Max_Time_ms,Speedup_Percent");

            for (int N : sizes) {
                System.out.println("\n-------------------------------------------------------------------------------");
                System.out.printf("Starting benchmark for N = %,d elements (Seed = %d, Trials = %d)...\n", N, SEED, TRIALS);
                System.out.println("-------------------------------------------------------------------------------");
                System.out.printf("%-6s | %-12s | %-12s | %-12s | %-12s | %-12s\n",
                        "Cutoff", "Mean (ms)", "StdDev (ms)", "Min (ms)", "Max (ms)", "Speedup (%)");
                System.out.println("-------------------------------------------------------------------------------");

                // Generate deterministic master array
                Integer[] masterArray = generateRandomArray(N, SEED);

                // Run GC once before starting the series and let JVM settle
                System.gc();
                try {
                    Thread.sleep(100);
                } catch (InterruptedException ignored) {}

                double baseTimeCutoff1 = 0.0;

                for (int cutoff = MIN_CUTOFF; cutoff <= MAX_CUTOFF; cutoff++) {
                    double[] times = new double[TRIALS];

                    for (int t = 0; t < TRIALS; t++) {
                        // Clone master array
                        Integer[] a = masterArray.clone();

                        // Precise timing of the sort routine only
                        long start = System.nanoTime();
                        Merge.sort(a, cutoff);
                        long end = System.nanoTime();

                        times[t] = (end - start) / 1_000_000.0;

                        // Correctness verification (outside timing interval)
                        if (!Merge.isSorted(a)) {
                            throw new IllegalStateException("Verification failed: array not sorted at Cutoff = " + cutoff);
                        }
                    }

                    // Statistical metrics
                    double mean = calculateMean(times);
                    double stdDev = calculateStdDev(times, mean);
                    double min = calculateMin(times);
                    double max = calculateMax(times);

                    if (cutoff == 1) {
                        baseTimeCutoff1 = mean;
                    }

                    double speedupPercent = ((baseTimeCutoff1 - mean) / baseTimeCutoff1) * 100.0;

                    // Output row to console
                    System.out.printf("%-6d | %12.3f | %12.3f | %12.3f | %12.3f | %+11.2f%%\n",
                            cutoff, mean, stdDev, min, max, speedupPercent);

                    // Output row to CSV
                    writer.printf(Locale.US, "%d,%d,%.4f,%.4f,%.4f,%.4f,%.2f\n",
                            N, cutoff, mean, stdDev, min, max, speedupPercent);
                    writer.flush();
                }
            }

            System.out.println("\nBenchmark complete! Results successfully saved to: " + csvFileName);

        } catch (IOException e) {
            System.err.println("Error writing to CSV: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void runWarmup() {
        System.out.println("Executing JVM Warm-up (" + WARMUP_RUNS + " runs) to trigger JIT C1/C2 compilation...");
        int warmupSize = 200_000;
        Random rng = new Random(12345);
        int[] sampleCutoffs = {1, 4, 7, 10, 16};

        for (int i = 0; i < WARMUP_RUNS; i++) {
            Integer[] arr = new Integer[warmupSize];
            for (int k = 0; k < warmupSize; k++) {
                arr[k] = rng.nextInt();
            }
            int cutoff = sampleCutoffs[i % sampleCutoffs.length];
            Merge.sort(arr, cutoff);
            System.out.println("  -> Warm-up iteration " + (i + 1) + "/" + WARMUP_RUNS + " completed (Cutoff = " + cutoff + ")");
        }
        System.gc();
        try {
            Thread.sleep(100);
        } catch (InterruptedException ignored) {}
        System.out.println("JVM Warm-up finished successfully.\n");
    }

    private static Integer[] generateRandomArray(int size, int seed) {
        Random rng = new Random(seed);
        Integer[] arr = new Integer[size];
        for (int i = 0; i < size; i++) {
            arr[i] = rng.nextInt();
        }
        return arr;
    }

    private static double calculateMean(double[] data) {
        double sum = 0.0;
        for (double val : data) {
            sum += val;
        }
        return sum / data.length;
    }

    private static double calculateStdDev(double[] data, double mean) {
        if (data.length <= 1) return 0.0;
        double sumSqDiff = 0.0;
        for (double val : data) {
            sumSqDiff += Math.pow(val - mean, 2);
        }
        return Math.sqrt(sumSqDiff / (data.length - 1));
    }

    private static double calculateMin(double[] data) {
        double min = Double.MAX_VALUE;
        for (double val : data) {
            if (val < min) min = val;
        }
        return min;
    }

    private static double calculateMax(double[] data) {
        double max = Double.MIN_VALUE;
        for (double val : data) {
            if (val > max) max = val;
        }
        return max;
    }
}
