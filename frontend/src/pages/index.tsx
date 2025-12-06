import React, { type ReactNode } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
// import HomepageFeatures from '@site/src/components/HomepageFeatures';
// import UrduTranslateButton from '@site/src/components/UrduTranslateButton';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <p className="hero__description">
          Physical AI & Humanoid Robotics is a comprehensive exploration of the cutting-edge intersection between artificial intelligence and advanced robotic systems. This book delves into how robots perceive, think, and act in the physical world, with a special focus on human-like forms and capabilities. From the fundamental principles of robotic movement and interaction to the complex ethical considerations of intelligent machines, we embark on a journey through the past, present, and future of bringing AI to life in physical form.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/chapter1"
          >
            Strat Reading ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />"
    >
      <HomepageHeader />
      {/* <UrduTranslateButton backendApiUrl={siteConfig.customFields?.backendApiUrl as string || 'http://localhost:8000'} /> */}
      <main id="docusaurus-main-content">
        {/* <HomepageFeatures /> */}
      </main>
    </Layout>
  );
}
