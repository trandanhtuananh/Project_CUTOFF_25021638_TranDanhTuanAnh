import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Random;

public class DatasetGenerator {

    public static void main(String[] args) {
        String dirPath = "datasets";
        File dir = new File(dirPath);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        int size = 10000;
        Random rng = new Random(42);

        // 1. Random dataset
        generateRandom(new File(dir, "random_10k.txt"), size, rng);

        // 2. Partially sorted dataset (~95% sorted, 5% random inversions/swaps)
        generatePartiallySorted(new File(dir, "partially_sorted_10k.txt"), size, rng);

        // 3. Reverse sorted dataset
        generateReverse(new File(dir, "reverse_10k.txt"), size);

        System.out.println("All datasets generated successfully in " + dir.getAbsolutePath());
    }

    private static void generateRandom(File file, int size, Random rng) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(file))) {
            for (int i = 0; i < size; i++) {
                writer.println(rng.nextInt(1_000_000));
            }
            System.out.println("Generated: " + file.getName() + " (" + size + " items)");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void generatePartiallySorted(File file, int size, Random rng) {
        int[] arr = new int[size];
        for (int i = 0; i < size; i++) {
            arr[i] = i * 2;
        }
        // Swap ~5% of elements randomly
        int numSwaps = size / 20;
        for (int i = 0; i < numSwaps; i++) {
            int idx1 = rng.nextInt(size);
            int idx2 = rng.nextInt(size);
            int tmp = arr[idx1];
            arr[idx1] = arr[idx2];
            arr[idx2] = tmp;
        }

        try (PrintWriter writer = new PrintWriter(new FileWriter(file))) {
            for (int val : arr) {
                writer.println(val);
            }
            System.out.println("Generated: " + file.getName() + " (" + size + " items)");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void generateReverse(File file, int size) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(file))) {
            for (int i = size; i >= 1; i--) {
                writer.println(i);
            }
            System.out.println("Generated: " + file.getName() + " (" + size + " items)");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
