require 'formula'

class Liblzf < Formula
  homepage 'http://software.schmorp.de/pkg/liblzf.html'
  url 'http://dist.schmorp.de/liblzf/Attic/liblzf-3.6.tar.gz'
  sha1 'd5cbc183999844627534ceaf68031f6b97688bd4'

  def install
    system "./configure", "--disable-debug", "--disable-dependency-tracking",
                          "--prefix=#{prefix}"
    system "make install" # if this fails, try separate make/make install steps
  end
end
