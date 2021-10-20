from conans import ConanFile, tools
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        boost_build_path = self.deps_user_info["b2"].boost_build_path.replace("\\", "/")
        tools.save("jamroot.jam", textwrap.dedent("""\
            ECHO "info:" Success loading project jamroot.jam file. ;
        """))
        tools.save("boost-build.jam", textwrap.dedent(f"""\
            boost-build "{boost_build_path}" ;
        """))
        self.run("b2 --debug-configuration", run_environment=True)
