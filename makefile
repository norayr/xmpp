VOC ?= voc
OFLAGS ?= -O2 -s -F
SOURCE := $(abspath $(dir $(firstword $(MAKEFILE_LIST))))
VOCSRC ?= $(abspath $(SOURCE)/../compiler)
BUILD ?= $(SOURCE)/build/2
BUILD := $(abspath $(BUILD))
MODULES := XmppTypes XmppConst XmppItems XmppXmlStream XmppXmlGen XmppConnections \
 XmppStrings XmppCore XmppMessenger XmppPresence XmppWire XmppSasl XmppClient
PKG_CONFIG ?= pkg-config
IDNA_LIBS ?= $(shell $(PKG_CONFIG) --libs libidn2)
NETWORK_CFLAGS = $(CFLAGS) -D_DEFAULT_SOURCE

ifneq ($(wildcard $(VOCSRC)/src/tools/make/modular-libraries.mk),)
include $(VOCSRC)/src/tools/make/modular-libraries.mk
NETWORK_MODULES := $(MODULAR_INTERNET) $(filter-out norayr/tls/httpsPure,$(MODULAR_TLS))
.PHONY: dependencies network-dependencies
dependencies:
	$(MAKE) -C "$(VOCSRC)/src/ports/xml" BUILD="$(BUILD)" VOC="$(VOC)" all
network-dependencies:
	$(MAKE) -C "$(VOCSRC)/src/ports/ooc" BUILD="$(BUILD)" VOC="$(VOC)" idna
	cd "$(BUILD)" && for name in $(NETWORK_MODULES); do \
		CFLAGS="$(NETWORK_CFLAGS)" $(VOC) $(OFLAGS) "$(VOCSRC)/src/ports/$$name.Mod" || exit; \
	done
else
dependencies:
	mkdir -p "$(BUILD)"
network-dependencies:
	@echo "Using installed XMLStream, IDNA and TLS13Live modules."
endif

.DEFAULT_GOAL := all
.PHONY: all test history-test network network-test probe tls-regression clean
all: dependencies
	cd "$(BUILD)" && for name in $(MODULES); do \
		$(VOC) $(OFLAGS) "$(SOURCE)/src/$$name.Mod" || exit; \
	done
test: all
	python3 "$(SOURCE)/tests/check-upstream.py"
	cd "$(BUILD)" && for name in TestXmppStream TestXmppCore TestXmppClient; do \
		$(VOC) $(OFLAGS) -m "$(SOURCE)/tests/$$name.Mod" && timeout 30 "./$$name" || exit; \
	done
history-test:
	python3 "$(SOURCE)/tests/check-history.py"
network: all
	@test "$$(uname -s)" = Linux || { echo "The XMPP TCP/TLS driver currently requires Linux."; exit 1; }
	$(MAKE) network-dependencies
	cd "$(BUILD)" && $(VOC) $(OFLAGS) "$(SOURCE)/src/XmppTCP.Mod"
network-test: network
	cd "$(BUILD)" && LDLIBS="$(LDLIBS) $(IDNA_LIBS)" $(VOC) $(OFLAGS) -m "$(SOURCE)/tests/TestXmppNetwork.Mod"
	python3 "$(SOURCE)/tests/loopback.py" "$(BUILD)"
probe: network
	cd "$(BUILD)" && LDLIBS="$(LDLIBS) $(IDNA_LIBS)" $(VOC) $(OFLAGS) -m "$(SOURCE)/tools/XmppProbe.Mod"
tls-regression: network
	@test -d "$(VOCSRC)/src/test/ports" || { echo "tls-regression requires VOCSRC to name a VOC checkout."; exit 1; }
	cd "$(BUILD)" && for name in norayr/strutils/strTypes norayr/strutils/strUtils \
		norayr/base64/StringBase64 $(MODULAR_HTTP) norayr/tls/httpsPure $(MODULAR_HTTPS) $(MODULAR_GEMINI); do \
		CFLAGS="$(NETWORK_CFLAGS)" $(VOC) $(OFLAGS) "$(VOCSRC)/src/ports/$$name.Mod" || exit; \
	done
	cd "$(VOCSRC)/src/test/ports" && sh ./tls/test.sh "$(VOC)" "$(BUILD)" 2 "-sFm"
	cd "$(VOCSRC)/src/test/ports" && sh ./gemini/test.sh "$(VOC)" "$(BUILD)" 2 "-sFm"
clean:
	rm -f $(foreach name,$(MODULES) XmppTCP XmppProbe TestXmppStream TestXmppCore TestXmppClient TestXmppNetwork,$(foreach ext,c h o sym,"$(BUILD)/$(name).$(ext)")) \
		"$(BUILD)/TestXmppStream" "$(BUILD)/TestXmppCore" "$(BUILD)/TestXmppClient" "$(BUILD)/TestXmppNetwork" "$(BUILD)/XmppProbe"
