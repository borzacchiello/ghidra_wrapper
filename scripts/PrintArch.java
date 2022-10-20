import ghidra.app.util.headless.HeadlessScript;
import ghidra.program.model.lang.Language;

public class PrintArch extends HeadlessScript {
	public void run() throws Exception {
		Language lang = currentProgram.getLanguage();
        System.err.println("Architecture: " + lang.getLanguageDescription().toString());
	}
}
